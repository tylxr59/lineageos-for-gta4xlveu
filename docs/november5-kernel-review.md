# November 5 legacy kernel and vendor review

Status: source/applicability review complete; full candidate build and device
validation in progress. Published/installed1793911332 is unchanged.

A full reread covers **97 November5 bulletin entries**, not only the original
seven-item kernel shortlist:31 kernel,3 Arm,12 Imagination,30 MediaTek,4 Unisoc,
9 public Qualcomm and8 closed-source Qualcomm. The self-authored
[coverage matrix](november5-coverage.json) records every entry and its scope.
Eight closed-source entries remain unverified at the device/firmware level;
**no full November5 patch-level claim is made**. Platform date remains2026-11-01.

Candidate kernel is `be84fa84d82073f331e94e8d21def1b2a90bd341` on
[security/los24-november5-20261105](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/tree/security/los24-november5-20261105),
based on released939ccbcb. The actively built CAF display fork is
[`64fd995`](https://github.com/tylxr59/android_hardware_qcom_display/commit/64fd9955352f7265ea8cb4bbd83991d972282046).
Both changes are source-pinned in [candidate manifest](../manifests/candidates/november5-final-20261105.xml)
and [seven fork pins](../manifests/candidates/november5-final-forks-20261105.xml).
All other1,240 project revisions are unchanged from release. Existing kernel
configuration, hardening, signing identity and compatibility override are retained.

## Kernel findings

The [initial bulletin triage](november-2026-candidate.md#kernelvendor-security-scope)
identified many absent or disabled implementations and seven items requiring
deeper legacy-path analysis. All public references for those seven were fetched,
including the supplementary fixes and prerequisite series. Those references
include alternative kernel-branch versions, so their count is not a patch count.

| Item | Current finding and action |
| --- | --- |
| CVE-2026-80604, HID | The normal `hid_input_report` rejects empty input, but exported `hid_report_raw_event` performs numbered-report lookup before checking that a report-ID byte exists. A narrow legacy guard is implemented in [0e4fbdfd4](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/0e4fbdfd4e3006c605b18e9796834b2d4030fdf3). This establishes a missing source boundary check, not a demonstrated reachable tablet exploit. |
| CVE-2026-43284, networking | The old representation is `tx_flags/SKBTX_SHARED_FRAG`. Copy, shift, GRO, segmentation and coalescing paths have corresponding marker-propagation gaps. Adaptations are [ffba1e414](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/ffba1e414ae794d668af938e787642bc147e2a32) and [9cde48f44](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/9cde48f446a0ec8ec43ad3b787aceec3e55fc16c). GRO is in skbuff.c here. The newer `tcp_clone_payload` helper is absent; the old MTU probe copies into linear storage, so unrelated modern TCP code was not imported. IPv4/IPv6 ESP are enabled. |
| CVE-2026-43499, rtmutex | Both relevant guards already exist: `remove_waiter` returns for a null waiter task, and the proxy-lock wrapper removes only for `ret < 0`. Existing baseline commit [a8306aea3](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/a8306aea3975b86678630be86d03e7c4b897c3be) records the backport. No redundant change staged. This resolves the specific previously outstanding source comparison, not general futex certification. |
| CVE-2025-38627, F2FS | The cited failure involves delayed decompression-context cleanup dereferencing an evicted inode. This tree's `f2fs_free_dic` frees page arrays directly and does not dereference an inode; the newer asynchronous cleanup and release helper are absent. The specific patched cleanup path is absent; no broad F2FS lifetime certification is claimed. No patch staged. |
| CVE-2026-89774, Bluetooth SCO | Tailored backport [ea6d573e1](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/ea6d573e1ae4bb3dc4e39713493d755a0800b7cf) includes the delayed-work sleeping-lock prerequisite, protected connection/listener reference acquisition, close/listener-state rechecks, balanced puts and the follow-up socket-before-connection lock order. Connection teardown also acquires its reference under the connection lock. Actual object compile and six deterministic function-model cases pass; no runtime certification yet. |
| CVE-2026-46242, epoll | The specific modern file-removal race is absent from this implementation. All three `ep_remove` callers were traced: epoll_ctl retains the monitored fdget reference; ep_free and eventpoll_release_file serialize under epmutex, and the latter still owns the file during __fput. The modern refcount/dying conversion which removed that serialization is absent. Do not import the unrelated prerequisite conversion. Bounded concurrent owned-watch close passes on baseline; candidate retest pending. |
| CVE-2026-64560, POSIX CPU timers | The specific pid-lookup race introduced by the modern conversion is absent. Timers retain a task reference, and __exit_signal still has the older has_group_leader_pid/de_thread workaround which clears group timers before sighand removal. The cited upstream message identifies that workaround as the predecessor to its affected pid-based conversion. The independent NULL-sighand cleanup visibility requirement is still applicable: [be84fa84d](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/be84fa84d82073f331e94e8d21def1b2a90bd341) adds the upstream release/acquire barrier pair without importing the modern PID lookup rewrite. Actual ARM64 exit/signal IR compiles; baseline has no NULL release-store/acquire pair, candidate emits both. Basic bounded timer lifecycle passes on baseline; no exec-race stress or general timer certification claimed. |

Primary fixes: [HID](https://android.googlesource.com/kernel/common/+/15475ee563738135a9978f2a0481b1cf972b3b72),
[network transfer](https://android.googlesource.com/kernel/common/+/f6d22ea6ae50acbc3f811a14fb2e55a2c129007d),
[Bluetooth SCO](https://android.googlesource.com/kernel/common/+/315636ba7cbf03382cfa7bd8887118f59fe96c5f),
[rtmutex](https://android.googlesource.com/kernel/common/+/5339d13d8b945cd5841d0e70728ee67474ea74f7),
[F2FS](https://android.googlesource.com/kernel/common/+/5d604d40cd3232b09cb339941ef958e49283ed0a),
[epoll terminal fix](https://android.googlesource.com/kernel/common/+/02f217a4bffc8a00313bf52ebb96003d7ae1d5d8),
[CPU timers](https://android.googlesource.com/kernel/common/+/585f2c9c9560f7e0dadafbba251183cea83d9dc4).

## Validation so far

Actual HID, networking and SCO ARM64 objects compile with the existing toolchain,
configuration and CFI/LTO flags, into isolated outputs. Focused tests compile
actual source functions/blocks with surrounding helpers modeled:

- HID entry: rejects empty numbered input before lookup; retains valid and
  unnumbered behavior. Released negative control fails, candidate passes.
- Network copy/coalescing: six cases cover shared marker propagation, destination
  bits, cloned fragments, linear copy and capacity rejection. Released negative
  control fails, candidate passes. This is not an actual kernel fragment test.
- SCO: six cases cover normal connect, socket/listener close interleavings,
  allocation failure and missing HCI; references/lock order are modeled. Released
  negative control fails, candidate passes.
- HDR: five actual-block boundary cases cover1025,UINT32_MAX,1024,1 and0 bytes.
  Oversized released negative controls fail; candidate cases pass. Copy helper
  instrumentation prevents the host tests from performing an overflow.

A temporary ordinary-ADB native helper passed baseline TCP copy/sendfile checks
(4MiB each),64 large UDP datagrams,256 concurrent epoll/watch close iterations,
and256 CPU-timer create/set/get/delete cycles. Only loopback and an immediately
unlinked owned scratch file are used. No external network, user-data access,
exploit, OOM or memory-pressure test. The helper was removed. Repeat on candidate.

The preceding snapshot passed full kernel/product build, strict VINTF, unchanged
policy, BTF/OOM/hardening and built HDR binary checks. Before device installation,
the independent timer ordering hunk was identified and added; earlier unsigned
artifacts and checks are preserved, signing stopped, and a fresh final snapshot
is rebuilding with all gates. A fresh full target-files/recovery/strict-VINTF build, BTF/OOM/hardening checks,
existing47-key signing/component/OTA checks and paired-image verification are
running. The first kernel-only graph attempt was stopped before expanding the
source snapshot to include the discovered active display fix; outputs are reused.
Signed candidate install, Android/hardware/runtime and matching-recovery/data
validation remain required. No candidate is published by this work.

## Qualcomm source and closed components

All nine public Qualcomm entries and supplementary references were retrieved
through CodeLinaro's public GitHub mirror after direct-host HTTP429 responses.
The first seven GPU/DSP entries target implementations absent here: KGSL shmem
reclaim/folio hooks, Gen8 snapshot tables, Gen7/8 hardware-scheduler command/fence
lists, newer FastRPC coredump global maps or async per-context perf counters.
The old DSP path waits synchronously, and getperfcounter returns file-owned
per-thread storage rather than ctx->perf. These are specific path findings, not
certification of all GPU/DSP code.

The complete bulletin also contains two display entries missed by the original
shortlist. CVE-2026-66113's SnapAllocCore is absent; the built ION BufferManager
returns validation/import errors without freeing/unmapping caller-supplied base
addresses. **CVE-2026-66114 has an equivalent gap in the built CAF sm8150 HWC**:
dynamicMetaDataLen reached memcpy without a capacity guard. The new display fork
bounds it before comparison/copy and recognizes length-only updates, following
[Qualcomm's fix](https://github.com/CodeLinaro-mirror/la_platform_vendor_opensource_display-core/commit/0a615ffd20a5677ca18acb53e9b4b1292b836078).
The similarly named hardware/qcom/sm8150 tree is not the selected HWC module;
module-info identifies hardware/qcom-caf/sm8150/display, which is what was fixed.

Arm CPU CVE-2025-0647's vendor CNA lists newer Neoverse/Cortex/C1 products rather
than this tablet's Kryo465/A55/A76 class. The other two Arm entries are Mali GPU
issues. Imagination, MediaTek and Unisoc implementations do not match this
Qualcomm/Adreno tablet. See the matrix for all per-entry classifications.

Eight Qualcomm closed-source entries remain **vendor coverage unverified**.
Some public CNA records are unavailable; others name newer components or broad
product lists without establishing this Samsung firmware's patch provenance.
The TPM2 reference-code item does not imply a TPM exists on the tablet
(CONFIG_TCG_TPM is disabled), but no blanket closed-firmware certification is
inferred from that. No newer maintained vendor blob head was found; the inherited
vendor patch date stays2025-05-01. Fixing open source does not establish the
missing device-specific firmware evidence or justify a2026-11-05 patch claim.
