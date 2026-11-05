# November 5 legacy kernel and vendor review

Started after publication of tested release **1793911332** on November 5, 2026.
The public release, feed, exact source pins and tablet are unchanged by this work.
The development changes below are **not installed or release-ready**. They do not
justify raising the advertised patch level from 2026-11-01.

Baseline kernel is `939ccbcb72b6c9143becd893a59cf84c3a1cf21d`, with the existing
4.14 backports, enabled configuration and compatibility override preserved.
Development branch: [security/los24-november5-20261105](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/tree/security/los24-november5-20261105),
currently `9cde48f446a0ec8ec43ad3b787aceec3e55fc16c`.
The normal checkout/local manifest remains at the released revision.

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
| CVE-2026-89774, Bluetooth SCO | All four bulletin references include reference-lifetime changes and a follow-up for sleeping under a spinlock. The old tree uses `bh_lock_sock` rather than the newer `lock_sock` design, so both lock order and reference ownership need a tailored review. No partially adapted fix staged. |
| CVE-2026-46242, epoll | The bulletin links a substantial refcount/removal prerequisite series and alternative-branch versions. The terminal fix pins the monitored file before taking its lock. The old implementation still serializes close/release with global `epmutex` and lacks the modern `dying`/refcount design. Review the old lifetime proof before importing the modern conversion or declaring non-applicability. No patch staged. |
| CVE-2026-64560, POSIX CPU timers | The new fix uses pid lookup/retry and memory-ordering changes. This tree stores a referenced task in `it.cpu.task`, acquired with `get_task_struct` and released on deletion. That differs from the fixed design, but older nonleader-exec and timer-list lifetime behavior still requires review. No coverage claim or patch staged. |

Primary fixes: [HID](https://android.googlesource.com/kernel/common/+/15475ee563738135a9978f2a0481b1cf972b3b72),
[network transfer](https://android.googlesource.com/kernel/common/+/f6d22ea6ae50acbc3f811a14fb2e55a2c129007d),
[Bluetooth SCO](https://android.googlesource.com/kernel/common/+/315636ba7cbf03382cfa7bd8887118f59fe96c5f),
[rtmutex](https://android.googlesource.com/kernel/common/+/5339d13d8b945cd5841d0e70728ee67474ea74f7),
[F2FS](https://android.googlesource.com/kernel/common/+/5d604d40cd3232b09cb339941ef958e49283ed0a),
[epoll terminal fix](https://android.googlesource.com/kernel/common/+/02f217a4bffc8a00313bf52ebb96003d7ae1d5d8),
[CPU timers](https://android.googlesource.com/kernel/common/+/585f2c9c9560f7e0dadafbba251183cea83d9dc4).

## Validation so far

Actual HID and networking ARM64 kernel objects compile using the existing
configuration, toolchain and CFI/LTO flags. Outputs were isolated from the normal
build products. A focused host test compiles the actual HID function entry through
the report lookup: the released entry fails the zero-length numbered-report
rejection assertion; the candidate passes. Valid numbered input and the existing
unnumbered entry behavior are preserved in that test. This is a control-flow test
with stubbed surrounding types/lookup, not execution inside the kernel.

Whole-kernel linking, complete ROM/recovery/signing, bounded shared-fragment
regressions, device networking and input/audio testing remain outstanding. No
exploit, deliberate OOM, root change, flash or tablet modification was performed
for this investigation. Source commits retain upstream attribution and identify
the adaptations and LLM assistance.

## Qualcomm and proprietary components

The seven Qualcomm entries in the initial review have public graphics/DSP/kernel
source references; they should not all be treated as proprietary-only blockers.
Fetching those references currently encounters HTTP429 throttling for most files.
One DSP patch, [3dacc0ac](https://git.codelinaro.org/clo/la/platform/vendor/qcom/opensource/dsp-kernel/-/commit/3dacc0ac01d64242ffb367c949b36b3e54368950)
for CVE-2026-57537, downloaded successfully. It locks/detaches newer
`frpc_coredump` global mappings. This tablet instead has the older
`drivers/char/adsprpc.c`; the named coredump/channel implementation is absent.
Equivalent older mapping/SSR lifetimes still need review; a different filename
alone does not establish non-applicability. Do not import its panic-on-error or
memory-ownership changes without reviewing the actual old implementation.

Closed-source firmware/library fixes remain a separate provenance and availability
question. No newer maintained vendor blob head was found in the final upstream
recheck. The inherited vendor patch date remains 2025-05-01. Download failures,
absent modern helpers and successful object compilation are not evidence of full
November5 coverage.

Next: bounded shared-fragment regression design and full kernel integration checks;
complete SCO, epoll and timer lifetime reviews; resume Qualcomm source inspection
when the source host permits downloads. Keep this work separate from the published
November1 platform release.
