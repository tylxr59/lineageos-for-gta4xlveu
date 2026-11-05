# November 2026 maintenance candidate

Status: **PUBLISHED; LOCAL AND PUBLIC VALIDATION COMPLETE**, November5,2026.
Corrected candidate **1793911332** is installed after signed no-wipe update.
Android unlock/data/setup/security, owner hardware, live kernel/display/BPF,
matching recovery/full partition hashes and powered-off charging retest passed.
Final Android return passed; the owned continuity marker and helpers are removed,
Rooted debugging is off, and the crash buffer is empty. The owner authorized publication of the exact tested signed build. Published
release/resolved pins and the11-entry feed now identify **1793911332**; all12
assets and fresh ROM/checksum downloads and host/tablet HTTPS feed matched.

## Source set

The final [exact candidate manifest](../manifests/candidates/november-charger-20261105.xml)
and [fork pins](../manifests/candidates/november-charger-forks-20261105.xml) include
the charger follow-updd2a0d3. The original
[candidate manifest](../manifests/candidates/november-20261105.xml) contains
1,242 projects. Eighty project identities/revisions differ from the released
manifest (including AOSP-to-Lineage fork renames). The merged November platform
security series supplies the **2026-11-01** patch level. API remains37.0;
Connectivity selection and the existing BPF override are unchanged.

- Media merge [`a7dd9c12`](https://github.com/tylxr59/android_frameworks_av/commit/a7dd9c12d2629fe100f09dc8f23e909bad1dca72) retains our codec owner fix while integrating five upstream media security commits through1c591473.
- Kernel merge [`939ccbcb`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/939ccbcb72b6c9143becd893a59cf84c3a1cf21d) retains releasedf0f9fc679 fixes and imports the shared Qualcomm base throughbae1ba425. Its delta includes the optional NXP SN driver/wiring and the maintained display-memory overlay removal. NXP_NFC_I2C depends on !NFC_NQ, while the tablet uses NFC_NQ.
- All candidate commits are pushed on `maintenance/los24-november-20261105` in their respective maintained forks.
- Device merge [`db669506`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/db669506d8002607452ff1c85627c7f7399899e0) includes QTI AIDL health/charger and recovery services, retires the standard HIDL Bluetooth audio implementation in favor of the already-present AIDL provider, and uses direct partition paths. It preserves strict VINTF kernel checks, QTI USB ownership, scoped credential policy, assisted GPS and thermal reporting. Vendor ec725c3, Pixel d4f83b6 and BPF c2621ec remain unchanged.
- The owner explicitly expanded scope to include and test the HAL/display changes. The initial platform-only build was stopped during graph generation; its log/manifests are retained separately. The expanded candidate completed compilation and signing. TI audio remains paused.

The source sync changed upstream project identities. Clean-worktree preflight,
resolved pre-sync sources and18 affected project metadata/ref snapshots were saved
privately before repo's required metadata migration. The AV merge required fetching
real shallow ancestry to recover the common base937eb904; no unrelated-history
merge or dropped local repair was used. Historical verified artifacts were retained.

## Build and signing

The owner initially requested a slow build, temporarily raised resources, resumed
gaming, then explicitly requested increased resources again. The final four-job
executor ran under a1200% total CPU quota,CPUWeight100,
IOWeight50 and best-effort7 disk I/O. Existing nice19 is retained. The soft memory limit was raised from28GiB to the existing32GiB hard ceiling
to clear BTF generation pressure; no OOM kill occurred. The generator phase
completed earlier with GOMAXPROCS8/GOMEMLIMIT24GiB/GOGC50; the main executor budget
is12GiB. Completed outputs are preserved through live resource changes.
No system package installation or persistent host power setting change is needed.
Temporary build/install inhibitors ended with their units.

The pipeline builds target-files/recovery/check-vintf-all, verifies exact source
pins, strict VINTF with real kernel inputs, paired XTRA config, thermal safety,
the exact display-memory overlay removal with fragment renumbering normalized, unchanged shared base DTB and unchanged audio/USB configuration, preserved legacy/proprietary libraries,
no extra permissive domains, compiled hardening defaults, BTF boundaries/type IDs
and actual OOM tracepoint layout. It then signs with the existing47 release
identities and verifies component and whole-file OTA signatures plus matching
boot/DTBO/recovery and vendor recovery payload. All listed host checks passed on the exact signed candidate. Compilation completed in3h15m29s with earlier owner-directed resource throttling. The archive contains zero native-test payload files; its four empty native-test directories match the released package. Target-files DTBO metadata has a regenerated AVB salt; the complete original image payload matches the compiled output and its packaged AVB hash verifies. Validator corrections are documented privately; no ROM rebuild/source change or compatibility bypass was used.

The connected baseline1793279242 was verified before installation. Both signed
candidates retained the marker checksum, encrypted-data unlock and setup/assistance
flags. Actual Android/recovery health, display range, owner hardware and BPF
regressions passed as detailed below. Thermal/XTRA configuration and proprietary
native bytes are preserved; no new exhaustive thermal or DNS/GNSS campaign is
claimed. No deliberate OOM, data wipe or manual vbmeta flash was performed.

## Kernel/vendor security scope

This is a **November1 platform** update. It does not claim all November5 kernel
or proprietary Qualcomm vulnerabilities are fixed. The bulletin's linked kernel
patches were inspected against the actual legacy source/config. A patch failing
to apply is not proof of non-applicability. The triage below records concrete
feature/config differences and outstanding legacy-path work; it is not a blanket
kernel CVE certification. No speculative kernel backports were added to force a
November5 claim. The inherited Samsung blobs and2025-05-01 vendor patch date are
unchanged, with no independently established current closed-source coverage.

Sources: [November bulletin](https://source.android.com/docs/security/bulletin/2026/2026-11-01),
[merged Lineage series](https://review.lineageos.org/q/topic:C_asb_2026-11+branch:lineage-24.0).

| Bulletin item | Legacy-source/config triage |
| --- | --- |
| CVE-2026-53256 | **disabled**: CONFIG_BT_RFCOMM is not set; the affected RFCOMM socket implementation is not built. |
| CVE-2026-59044 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-59045 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-80604 | **requires legacy-path review**: The modern __hid_report_raw_event/bufsize helper is absent; the old hid_input_report checks nonzero size before report lookup. The exported hid_report_raw_event needs separate call-path review; no non-applicability certification. |
| CVE-2026-89774 | **requires legacy backport review**: The SCO implementation exists but predates the modern lifecycle/context in this patch. Do not apply with relaxed context or claim it fixed. |
| CVE-2026-59048 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2025-38627 | **different implementation; no coverage claim**: F2FS compression is enabled, but this tree has an older f2fs_free_dic with direct kfree cleanup, not the newer asynchronous inode-dependent cleanup changed by the patch. Related lifetime review is not exhaustive. |
| CVE-2026-23240 | **disabled**: CONFIG_TLS is not set. |
| CVE-2026-31533 | **disabled**: CONFIG_TLS is not set. |
| CVE-2026-43284 | **requires legacy backport review**: Legacy skb uses tx_flags/SKBTX_SHARED_FRAG, not modern flags/SKBFL_SHARED_FRAG. Transfer-helper correctness must be reviewed against the older APIs. |
| CVE-2026-43499 | **different implementation; partial guard already present**: rt_mutex_start_proxy_lock already tests ret < 0; the newer rt_mutex_base/rtmutex_api split and waiter enqueue handling differ. No exhaustive rtmutex vulnerability certification. |
| CVE-2026-46242 | **requires legacy series review**: The linked epoll refcount conversion depends on newer epitems/list and lifetime changes. A complete backport/prerequisite review is not established. |
| CVE-2026-58824 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-58825 | **affected implementation absent**: The new per-process task/mm/files dmabuf_info accounting is absent. Existing DMA-BUF iterator/accounting backports use a different implementation; this is not a certification of all DMA-BUF code. |
| CVE-2026-58826 | **affected implementation absent**: The new per-process task/mm/files dmabuf_info accounting is absent. Existing DMA-BUF iterator/accounting backports use a different implementation; this is not a certification of all DMA-BUF code. |
| CVE-2026-58827 | **affected implementation absent**: The new per-process task/mm/files dmabuf_info accounting is absent. Existing DMA-BUF iterator/accounting backports use a different implementation; this is not a certification of all DMA-BUF code. |
| CVE-2026-58828 | **affected implementation absent**: The new per-process task/mm/files dmabuf_info accounting is absent. Existing DMA-BUF iterator/accounting backports use a different implementation; this is not a certification of all DMA-BUF code. |
| CVE-2026-58829 | **affected implementation absent**: fs/fuse/backing.c and fuse_backing_mmap are absent; no FUSE-BPF backing implementation is installed. |
| CVE-2026-58844 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-58845 | **affected implementation absent**: Android pgsize_migration/vma padding implementation is absent; current kernel uses 4KiB pages. |
| CVE-2026-58847 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-58942 | **affected implementation absent**: Android vma_data_pages ELF padding implementation referenced by this fix is absent. |
| CVE-2026-59042 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-59043 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-64011 | **disabled**: CONFIG_NFC is not set, so the generic LLCP socket implementation is not built. Vendor NFC_NQ is separate. |
| CVE-2026-64427 | **disabled**: CONFIG_HID_LOGITECH is not set; the newer Logitech DJ report validation also differs. |
| CVE-2026-64560 | **requires legacy lifecycle review**: This 4.14 POSIX CPU timer implementation predates the newer cpu_timer_task_rcu/pid-based lifecycle in the patch. No coverage claim without reviewing the older task-reference design. |
| CVE-2026-46232 | **affected driver absent**: drivers/hid/hid-playstation.c is absent; do not confuse it with the older Sony driver. |
| CVE-2026-23184 | **affected implementation absent**: binder_netlink_report and BR_TRANSACTION_PENDING_FROZEN are absent from this binder tree. |
| CVE-2026-59046 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-59047 | **affected pKVM implementation absent**: The Android pKVM implementation or specific protected-guest/IOMMU path is absent from this 4.14 tree. |
| CVE-2026-25291 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |
| CVE-2026-25301 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |
| CVE-2026-57537 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |
| CVE-2026-57545 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |
| CVE-2026-57548 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |
| CVE-2026-57549 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |
| CVE-2026-57554 | **unverified vendor applicability**: Qualcomm bulletin source applies to newer downstream component branches. Device-specific matching/backport coverage is not established; closed-source blobs remain unchanged. |

Host DTBO validation note: stock fdtoverlay reports FDT_ERR_BADOVERLAY even for
the released, hardware-tested base/overlay pair. No successful host overlay
application is claimed. The candidate gate instead compares every parsed overlay
property after normalizing the expected fragment renumbering, requires only the
specific dump-region override to disappear, and verifies the unchanged base DTB
still contains its original dump node/range. Actual recovery/Android boot and
live partition hashes remain required.

## Initial candidate1793891339 artifact evidence — November5

ROM SHA256: `fce0e47849d02e76da2f5aa4fee04a844f0cd2c32b70c5c3818c0da8f9a01ebb`.
Kernel: `4.14.357-openela-perf-g939ccbcb72b6`. Existing release OTA certificate
pin is unchanged. Component verification passed120 standalone APKs,37 signed
APEX containers/payloads and26 nested APKs, retaining the presigned CTS shim.
Actual recovery has one matching OTA trust certificate. Whole-file OTA signature,
signed boot/DTBO images and the matching vendor recovery payload/updater pass.
Strict VINTF, expected overlay removal with unchanged shared base DTB, BTF/type
bounds, OOM field layout and compiled hardening defaults pass. Candidate and
released enabled kernel configurations match;784 compared proprietary native
entries and all nine legacy compatibility libraries remain byte-identical.
No full November5 kernel/vendor security certification is claimed.

Signed installation returned exit0 without a wipe, and actual Android timestamp,
kernel and embedded/live config match. Original live vbmeta and actual matching
recovery partition hashes were subsequently verified. The continuity marker
survived both candidates and recovery/charger round trips, then was removed after
final Android checksum verification.

## Device validation progress

Owner confirmed usual setup, Wi-Fi/video, both cameras, speakers/AirPods routing,
S Pen, rotation, sleep/wake, USB file transfer and charging. Android live device
 tree confirms the inherited display reservation at0x9c000000, size23MiB.
The real OOM field ABI and system_server attachment,14 network hooks, both ABI
wakelock suites (6pass/2expected skips each), production accounting and bounded
DMA-BUF1024/churn/200early-close/no-owned-leak tests pass. No deliberate OOM or
pressure test was performed. No captured kernel failure patterns; crash buffer
empty. Temporary helpers removed and Rooted debugging disabled afterward.

Actual recovery kernel/config and full boot/DTBO/recovery partition hashes match
the signed candidate. Original vbmeta is unchanged. The new QTI recovery health
service runs, battery is healthy/full, and the display reservation matches.
Powered-off charging failed initially and passed after the follow-up below.
Final Android unlock/data cleanup passed. The exact corrected candidate is now published.

## Powered-off charging failure and follow-up

The owner observed the charging ring alternating with the packaged question-mark
`battery_fail.png` during wall-powered offline charging. This test failed; normal
Android charging and the recovery battery check do not establish charger-mode
success. Android subsequently returned with unlocked encrypted data, continuity
marker intact, enforcing SELinux, Rooted debugging off and an empty crash buffer.

The installed compiled policy permits normal `hal_health_default` to read the
Samsung `sysfs_battery` files, but has no corresponding read/open/getattr allow
for `charger_vendor`, the new QTI offline charger domain. This is a concrete
policy gap and a plausible explanation for the unavailable-battery image; retained
charger-log fragments support that diagnosis, but the persisted text is corrupted
and provides no fully intact matching denial line. Device fix
[`dd2a0d3`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/dd2a0d39a3929c63d2b00cb8c6f31e39134255c5)
adds only read-only battery-file access for that domain. SELinux remains enforcing.
Fresh candidate manifests are `november-charger-20261105.xml` and
`november-charger-forks-20261105.xml`; kernel/AV/vendor/Pixel/BPF pins are unchanged.

The incremental full ROM/recovery build completed in10m43s. All host checks and
existing-key signing/component/OTA verification passed, including the explicit
packaged-policy access gate. Corrected build1793911332 installed no-wipe/exit0
and booted with unlocked encrypted data, matching marker/setup/config, enforcing
SELinux, normal ADB, Rooted debugging off and empty crash buffer. Boot/DTBO hashes
are identical to the preceding candidate; recovery includes the policy fix.
ROM SHA256: `fce3f4dcb022cecd98204fa8f21e12b80f9823e4bffd868f29b4a40eb9ae3651`.
Previous signed artifacts and test evidence are preserved. Matching recovery kernel/config/full partition hashes and actual corrected policy
passed; original vbmeta unchanged. Owner confirmed powered-off charging now works
normally. Final Android return, marker checksum and setup/assistance flags pass.
The owned marker was removed after verification; helpers are absent, screen-awake
setting0, normal UID2000, Rooted debugging off, unlocked FBE, enforcing SELinux and
empty crash buffer. Build/install units ended successfully.
Owner-authorized [publication](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261105-gta4xlveu-1793911332) completed without rebuild/re-sign/newkeys.

## Final upstream recheck

After local validation on November5, a fresh read-only comparison of306 selected
moving upstream heads found all runtime source heads included in1793911332.
The platform manifest head is unchanged. Device/vendor forks, shared Qualcomm
kernel, media, Pixel HAL and BPF heads are ancestors of the candidate pins.
The sole new nonincluded commit is LineageOS/charter main
[`9ee719ec`](https://github.com/LineageOS/charter/commit/9ee719ec4a84fb72cbc04725e55c0da833fe6db6),
which changes only AI contribution guidance. It changes no ROM code and does not
require rebuilding this tested candidate. Fixed AOSP inputs remain manifest-tag
selected. This up-to-date branch comparison does not resolve the separate legacy
kernel/vendor coverage limitations documented above.
