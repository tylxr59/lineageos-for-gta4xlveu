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


## First device result: rejected

Signed candidate1792935924 compiled and passed strict VINTF, persistent-key
component/whole-OTA signatures, actual embedded kernel configuration checks and
all nine offline field relocations against the final ROM kernel. DTBO, USB,
SELinux policy and the thermal HAL matched working1792933707. Its only kernel
config changes were DEBUG_INFO_BTF and DMABUF_BPF_ITER.

The no-wipe sideload succeeded, but the owner reported a bootloop. **Do not
install or publish this unchanged candidate.** Boot and actual Android loader/
accounting tests did not pass. The known-good1792933707 recovery was restored
without changing vbmeta or formatting data, to collect failure evidence and
restore the working full ROM. The full known-good signed1792933707 ROM was then restored without wiping.
Android boot, unlocked encrypted data/test file, enforcing SELinux, UID2000 and
Rooted debugging off were rechecked.
Compilation and offline relocation checks were insufficient to establish boot.


## Demonstrated BTF parser mismatch and follow-up

The failed-boot log reached Android's critical networking BPF loader. Kernel
validation reported `hdr_len not found`, then `in-kernel BTF is malformed`, so
networking programs could not load. This was not evidence of the DMA-BUF
iterator running and crashing: the earlier common BTF setup was unusable.

The inherited parser used weak `_binary__btf_vmlinux_bin_start/end` symbols,
which were undefined in the actual linked kernel. The linker and sysfs reader
instead use `__start_BTF` and `__stop_BTF`. Thus host tools could inspect valid
BTF from the ELF/sysfs layout while the internal parser saw a zero-length span.
[4823beeb2](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/4823beeb2)
makes both consumers use the real section boundaries, retaining header/type
validation.

Further review before another install found 16-bit type/string limits in the
inherited UAPI. The generated metadata has approximately173,538 types and4.1MiB
of strings, exceeding both. The limits now match the standard values carried
by pinned Android/Linux BTF UAPI: 20-bit type IDs and24-bit string offsets.
The metadata walk also now propagates a failed type-table allocation instead
of continuing with an incomplete table. Both fixes are in
[8861e8c76](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/8861e8c76).
The symbol-only intermediate build was stopped; it was never installed.

The follow-up host guard inspects the actual parser object and final ELF:
obsolete weak references must be absent, both real boundaries defined, their
span equal to the emitted BTF section, and header/type/string counts within the
actual consumer limits. Supported kinds remain1–15; no invalid metadata or
allocation error is ignored to make a program load. This improves the preflight
checks but still requires real kernel/Android loader validation after building.
The parser-repair full ROM compiled and passed these checks and signing, but
was superseded before installation by the additional type-name repair below.


## Typed helper metadata identity

Review traced duplicate `seq_file` graphs through `perf_event.rb` to two different
structures both named `ring_buffer` (perf and tracing). In the parser-repair
bundle, iterator metadata's sequence pointer and the typed printing helper
resolved to different `seq_file` IDs. Re-running ordinary libbpf deduplication
preserved that ambiguity. This is not solved by ignoring typed-pointer checks.

Linux already fixed this class of collision in
[56de4e8f9146, perf: Make struct ring_buffer less ambiguous](https://github.com/torvalds/linux/commit/56de4e8f9146680bcd048a29888f7438d5e58c55).
The local backport [4c536a5bc](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/4c536a5bc)
renames only perf's tag to `perf_buffer` in four files (64 occurrences).
A token-substitution comparison confirms no field, executable statement or
function name changed. CFI-aware compilation and device tests remain necessary.

The next build's guard additionally requires a unique `seq_file` definition and
identical IDs for the iterator's real metadata field and the compiled typed
helper's BTF ID entry. The guard correctly rejects the pre-rename bundle.
The previous host-only bundle was never installed. The complete candidate with
all repairs is now building separately; public release/feed remain unchanged.
