# Device-source freshness audit

Live GitHub checks on2026-10-24 compared the installed release1792787032 source
pins, rather than the local experimental audio branches. No source branch was
merged, no build started and no tablet software changed.

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
