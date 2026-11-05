# November 2026 maintenance candidate

Status: **BUILDING**, November 5, 2026. Source/build preparation is authorized.
The installed and published release remains **1793279242**; this candidate is
not installed, hardware-validated or approved for publication.

## Source set

[Exact candidate manifest](../manifests/candidates/november-20261105.xml) contains
1,242 projects. Eighty project identities/revisions differ from the released
manifest (including AOSP-to-Lineage fork renames). The merged November platform
security series supplies the **2026-11-01** patch level. API remains37.0;
Connectivity selection and the existing BPF override are unchanged.

- Media merge [`a7dd9c12`](https://github.com/tylxr59/android_frameworks_av/commit/a7dd9c12d2629fe100f09dc8f23e909bad1dca72) retains our codec owner fix while integrating five upstream media security commits through1c591473.
- Kernel merge [`939ccbcb`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/939ccbcb72b6c9143becd893a59cf84c3a1cf21d) retains releasedf0f9fc679 fixes and imports the shared Qualcomm base throughbae1ba425. Its delta includes the optional NXP SN driver/wiring and the maintained display-memory overlay removal. NXP_NFC_I2C depends on !NFC_NQ, while the tablet uses NFC_NQ.
- All candidate commits are pushed on `maintenance/los24-november-20261105` in their respective maintained forks.
- Device merge [`db669506`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/db669506d8002607452ff1c85627c7f7399899e0) includes QTI AIDL health/charger and recovery services, retires the standard HIDL Bluetooth audio implementation in favor of the already-present AIDL provider, and uses direct partition paths. It preserves strict VINTF kernel checks, QTI USB ownership, scoped credential policy, assisted GPS and thermal reporting. Vendor ec725c3, Pixel d4f83b6 and BPF c2621ec remain unchanged.
- The owner explicitly expanded scope to include and test the HAL/display changes. The initial platform-only build was stopped during graph generation; its log/manifests are retained separately. The expanded candidate is building under the same resource limits. TI audio remains paused.

The source sync changed upstream project identities. Clean-worktree preflight,
resolved pre-sync sources and18 affected project metadata/ref snapshots were saved
privately before repo's required metadata migration. The AV merge required fetching
real shallow ancestry to recover the common base937eb904; no unrelated-history
merge or dropped local repair was used. Historical verified artifacts were retained.

## Build and signing

The owner initially requested a slow build, temporarily authorized more resources,
then resumed gaming. The existing four-job executor now continues without restart
under a150% total CPU quota,CPUWeight1,IOWeight1, with every running thread moved
to nice19/idle I/O. Future children inherit those priorities. MemoryHigh24GiB,
MemoryMax32GiB and the existing swap ceiling are retained rather than shrinking
an active compiler's memory. The generator phase completed at higher resources;
its GOMAXPROCS8/GOMEMLIMIT24GiB/GOGC50 budget and the main executor's12GiB budget
remain recorded. Completed compilation outputs are preserved.
No system package installation or persistent host power setting change is needed.
A temporary sleep inhibitor follows the pipeline lifetime.

The pipeline builds target-files/recovery/check-vintf-all, verifies exact source
pins, strict VINTF with real kernel inputs, paired XTRA config, thermal safety,
the exact display-memory overlay removal with fragment renumbering normalized, unchanged shared base DTB and unchanged audio/USB configuration, preserved legacy/proprietary libraries,
no extra permissive domains, compiled hardening defaults, BTF boundaries/type IDs
and actual OOM tracepoint layout. It then signs with the existing47 release
identities and verifies component and whole-file OTA signatures plus matching
boot/DTBO/recovery and vendor recovery payload. These are planned checks until
the result is recorded; build start is not a successful compilation claim.

The connected baseline tablet was verified on1793279242 with boot complete, unlocked file encryption, normal UID2000, enforcing SELinux and Rooted debugging off. Ordinary ADB service/display/battery/USB snapshots and setup flags are retained privately. An owned continuity marker was created and checksum verified. No candidate has been installed. Device validation remains pending after a signed candidate passes host checks.
It must additionally cover the QTI AIDL health service in Android/recovery, battery/charging behavior and charger mode, Bluetooth audio, display/suspend/wake and the compiled display-memory range. It must cover signed no-wipe update, original pattern and encrypted-data/setup
continuity, enforcing SELinux, normal ADB/rooted-debugging off, Android/recovery
boot and full image verification, hardware smoke, USB/MTP, Bluetooth, thermal,
assisted GPS and retained BPF behavior. No deliberate OOM or data wipe is planned.

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
