# Device-source freshness audit

Live GitHub checks on2026-10-24 compared the installed release1792787032 source
pins, rather than the local experimental audio branches. The initial read-only audit did not change sources or the tablet. The later
owner-requested maintenance candidate is recorded separately below.

## Maintained device repositories

| Component / installed pin | Against Sevenrock lineage-24.0 | Against gta4xlve-dev lineage-23.2 |
| --- | --- | --- |
| Device `eb9bc69` | 6 ahead, 0 behind | 21 ahead, 0 behind |
| Kernel `75a416868` | 1 ahead, 0 behind | 54 ahead, 0 behind |
| Vendor `4388d72` | Identical | Identical |

The maintained vendor repositories contain no newer commit to import. Fork
nesting itself does not imply stale source: compare the actual commit ancestry.
These GitHub repositories still default to lineage-23.2, but the build manifest
pins the intended commits explicitly. Do not replace them with the default
branch or assume the displayed branch determines the installed Android version.

## Shared Lineage kernel base: 18 commits pending review

Our kernel contains the shared Lineage base through
`f136eaf93d6285680e683d7827c690ecc5c28b54`. The shared repository's maintained
branch is historically named **lineage-20**, not lineage-24.0. Its current tip
is `285869032633b3de3c6bdefd8f3b553f988c11da`:
[fixed source comparison](https://github.com/LineageOS/android_kernel_qcom_sm8150/compare/f136eaf93d6285680e683d7827c690ecc5c28b54...285869032633b3de3c6bdefd8f3b553f988c11da).

The 18 commits dated October4–5 address cgroup initialization, string handling,
reference counting, delegation, and freezer/signal state handling. They affect
nine files, with146 insertions and111 deletions. Patch-equivalence comparison
confirmed these commits are not already present in the installed Samsung
kernel. `CONFIG_CGROUP_FREEZER=y` in the build configuration.

A `git merge-tree --write-tree` preview against the installed kernel pin completed
without conflicts. That writes a preview tree only: it is not a source-branch
merge, successful build, boot test, security certification or demonstrated
battery fix. Review and build a separate maintenance candidate, retaining the
bootloader reserved-memory fix and other working Samsung adaptations. Begin
from the installed kernel source if the owner has not resumed the separate TI
audio integration. Do not accidentally include its paused experimental commit.

## Samsung vendor/firmware boundary

The device configuration reports vendor security level2025-05-01; Android's
platform security level is separate. Samsung's published SM-P613 histories for
[XAR](https://doc.samsungmobile.com/SM-P613/023882220819/eng.html) and
[BTU](https://doc.samsungmobile.com/SM-P613/023399220804/eng.html), checked during
this audit, both list `P613XXS8CYE1` / Android14 / May2025 security as their latest
entry. XAR lists a June2 release and BTU May27. EUX access was denied; this is not
a claim that every regional firmware catalog or individual proprietary binary
was exhaustively compared. Matching a reported patch date does not establish
that every retained blob is from that exact firmware package.

There is no demonstrated newer maintained vendor drop to install. Samsung's
closed components do not become new Android17 implementations merely because
our Android platform is newer. Import any future same-device vendor release as
a separate compatibility change, with source provenance and hardware validation.


## Combined maintenance candidate (2026-10-24)

After the successful [CFI enforcement test](vintf-audit.md#first-enforcement-candidate-2026-10-24),
the owner requested current upstream changes in the same candidate. The
[exact candidate manifest](../manifests/candidates/maintenance-20261024.xml)
pins all 1,242 projects. It is separate from the published release manifest.

Device `12c0e2db5ea75f284b144db2322738a01f6231fd`, kernel
`88b63b7aeb73fc983a9a13f76601135a9950cb89`, and unchanged vendor `4388d72`
are available in the owner's forks; device/kernel branch is
`fix/los24-maintenance-20261024`. The kernel integrates the reviewed 18 commits
through shared Lineage base `285869032633b3de3c6bdefd8f3b553f988c11da`.
The merge was clean and retains the Samsung boot fixes and enforcing CFI.
Paused TI audio changes are excluded.

Platform sync used LineageOS/android lineage-24.0 manifest head
`b51a0c449a3279ca55fb6d4d91d2143e42e2fff5`. Eighteen project revisions differ
from the published baseline: two maintained forks and sixteen platform/support
repositories, with 30 upstream commits across the latter. Changes include:

- Chromium WebView 156.0.8078.47 and matching patches/prebuilts.
- Conscrypt blocklist/parser changes and a Lineage SDK Bluetooth attribution fix.
- Camera QHD option handling, fingerprint logging and upstream health metadata.
- Other-device audio/configuration changes, APN migration and maintenance metadata.

The selected Soong, Go, build and toolchain pins did not change. Android's
reported security patch remains 2026-10-01; vendor remains 2025-05-01. QHD UI
changes do not establish hardware recording support, and cgroup fixes do not
establish a measured battery improvement.

Full target-files/recovery compilation and `check-vintf-all` passed in 16m33s.
Strict VINTF checks use the real enforcing-CFI kernel configuration, matching
the embedded kernel and live Android config. Same-key signing and whole-file,
component, recovery trust and AVB checks passed. Signed build `1792851872`
installed without wiping and booted kernel
`4.14.357-openela-perf-g88b63b7aeb73`. Android data unlocked; the saved-file
checksum survived, SELinux stayed enforcing, ADB remained UID2000 and Rooted
debugging stayed off. The initial crash buffer was empty and the new WebView
version was present. The owner confirmed their existing pattern/setup, Wi-Fi,
both cameras, speakers, S Pen and general operation.

The automatically updated recovery also booted; full boot/DTBO/recovery
partition hashes and its live kernel configuration match the signed images.
A recovery-menu reboot returned to Android; original pattern/setup, saved-file
checksum and the same security checks passed again. This is a locally installed
candidate; public release manifests and the OTA feed still identify `1792787032`.
