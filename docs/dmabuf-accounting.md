# DMA-BUF accounting candidate

DMA-BUFs hold shared display, camera and video buffers. Android 17 tries to read
its per-buffer totals through a privileged BPF iterator. The released kernel
has neither that target nor built-in BTF metadata, and its sysfs fallback is
also absent. This explains the repeated accounting errors; it does not by itself
show a memory leak or broken playback.

## Candidate source

The isolated experiment is now being prepared for a full signed ROM test.
Kernel branch `fix/los24-dmabuf-candidate` retains the released CFI, KPTI and
kernel-log restrictions. It includes the earlier BTF host-tool and conditional
fault-injection-ID repairs, plus:

- [52847c63d](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/52847c63d): retain the next unconsumed buffer across legacy reader boundaries and release it on early close.
- [0618060fb](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/0618060fb): enable BTF and the optional DMA-BUF iterator in this device's candidate config.
- [40dd1806a](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/40dd1806a): host lifecycle regression harness against the actual iterator source.
- [1d5531f9a](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/1d5531f9a): use pinned LLVM archiver/linker tools in Android's restricted build PATH.

The initial modern seq-file adaptation compiled, but its start-at-position-zero
behavior was insufficient for this older `bpf_seq_read`: that reader stops at
caller read limits and invokes stop with an unconsumed next object. Without a
per-open resume reference, later reads silently end early. The candidate now
transfers that reference back on start and releases it in the private-state
close callback. It holds at most one buffer between reads, not a snapshot of all
allocations. The global list is locked only while acquiring the next reference;
the previous reference is released after unlocking.

All nine field relocations in the actual built Android `dmabufIter.bpf` object
resolved against the experimental kernel BTF with the installed host bpftool
(libbpf 1.8). This is an offline field-layout check, not execution by Android's
pinned libbpf 1.4.5 or proof of kernel verifier acceptance. Host ASan/UBSan tests
cover empty/single/1,000-buffer traversal, small batches, EOF and early close.
They stub the allocator/BPF interfaces and do not establish kernel race safety.

The first Android-integrated build found that plain `ar`, `ld` and pkg-config
were absent from its restricted PATH. The source helper now selects the pinned
LLVM tools and links its native libelf/zlib dependencies explicitly. No host
package installation or global PATH relaxation is required.

## Device validation required

Before calling this fixed:

1. Build and sign the complete ROM/recovery with the persistent release keys;
   verify strict VINTF, configuration, signatures and matching recovery payload.
2. Install without wiping. Confirm boot, saved pattern/data and hardware smoke
   checks with enforcing SELinux and CFI/KPTI retained.
3. Verify BTF initialization, Android's real BPF loader success and the expected
   pinned iterator. Check `dmabuf_dump -b` and framework totals, not just absence
   of log messages.
4. Allocate 1,024 ordinary 4-KiB system-heap buffers (4 MiB), retaining their
   descriptors. Confirm each known inode/size appears exactly once with 1, 17,
   4,096 and 65,536-byte read requests. Run concurrent allocation/free and
   early-close tests; after closing owned buffers none may remain pinned by
   leaked iterator references. Keep the native probe temporary and bounded.
5. Exercise video and cameras during repeated collection, then check stability,
   crashes, policy denials and idle behavior. Long-term stress/suspend power
   remain separate from a short smoke test.
6. Verify automatic recovery updating/full partition hashes and recovery-menu
   Android return. Remove probes and restore Rooted debugging off.

Current full-build/device results belong in the validation record below. No
public feed/source release pin advances until a tested release is requested.
The userspace BPF kernel-version override is unchanged; this targeted iterator
work does not certify every modern BPF feature. Audio experiments are excluded.

Use the previous signed full ROM and its matching recovery for rollback. Preserve
userdata and the original vbmeta. Do not install an isolated boot-only candidate:
the existing vendor recovery updater can replace recovery with an incompatible
image during diagnostics; see the hardening investigation/runbook.
