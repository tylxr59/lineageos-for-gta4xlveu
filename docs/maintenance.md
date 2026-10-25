# Updating upstream and shipping a release

The intended operator workflow is a request such as **“get us up to date with
mainline LineageOS and push an update.”** An agent should carry that request
through publication once the following evidence is in place. Source compilation
alone is not a release success criterion.

## Start here: request scope and update sources

**“Check/look for updates”** means fetch current upstream information, compare
it with the last released source, and report applicable changes and validation
needed. It does not request installation or publication. **“Update and push an
OTA”** means carry the reviewed changes through the release workflow below.
A new Android/LineageOS major version is a separate porting task.

Start from the current release's source manifest and
[`manifests/resolved.xml`](../manifests/resolved.xml). The three maintained fork
pins are in [`manifests/gta4xlveu.xml`](../manifests/gta4xlveu.xml). Check
[`ota/gta4xlveu.json`](../ota/gta4xlveu.json), the matching
[release assets](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases),
[testing](testing.md), and any local progress record to establish what was
actually shipped and installed. Local HEAD, a newer experiment or a repository's
default branch is not automatically the released baseline.

### Exact upstream map

| Layer | Where to check | Branch / interpretation |
| --- | --- | --- |
| LineageOS platform manifest | [LineageOS/android](https://github.com/LineageOS/android/tree/lineage-24.0) | `lineage-24.0` for routine LOS24 updates. Review changes to all manifest-selected projects, including projects whose own commits changed without a manifest-file change. |
| Shared Qualcomm kernel base | [LineageOS/android_kernel_qcom_sm8150](https://github.com/LineageOS/android_kernel_qcom_sm8150/tree/lineage-20) | **`lineage-20`** is the historical kernel branch we inherit. Do not guess `lineage-24.0` from the Android version. |
| Device integration | [sevenrock/android_device_samsung_gta4xlveu](https://github.com/sevenrock/android_device_samsung_gta4xlveu/tree/lineage-24.0) and [gta4xlve-dev/android_device_samsung_gta4xlveu](https://github.com/gta4xlve-dev/android_device_samsung_gta4xlveu/tree/lineage-23.2) | Sevenrock `lineage-24.0`; original maintainer `lineage-23.2`. Review both against our device pin. |
| Samsung kernel integration | [sevenrock/android_kernel_samsung_gta4xlve](https://github.com/sevenrock/android_kernel_samsung_gta4xlve/tree/lineage-24.0) and [gta4xlve-dev/android_kernel_samsung_gta4xlve](https://github.com/gta4xlve-dev/android_kernel_samsung_gta4xlve/tree/lineage-23.2) | Sevenrock `lineage-24.0`; original maintainer `lineage-23.2`. Check these **in addition to** the shared Lineage kernel base. |
| Proprietary vendor files | [sevenrock/android_vendor_samsung_gta4xlveu](https://github.com/sevenrock/android_vendor_samsung_gta4xlveu/tree/lineage-24.0) and [gta4xlve-dev/android_vendor_samsung_gta4xlveu](https://github.com/gta4xlve-dev/android_vendor_samsung_gta4xlveu/tree/lineage-23.2) | Sevenrock `lineage-24.0`; original maintainer `lineage-23.2`. A new commit must be reviewed for blob provenance and device compatibility. |
| Samsung firmware provenance | Official SM-P613 [XAR history](https://doc.samsungmobile.com/SM-P613/XAR/doc.html) and [BTU history](https://doc.samsungmobile.com/SM-P613/BTU/doc.html) | Follow the English history/iframe (`dflt_page`) if the wrapper is empty. Record region, firmware build and vendor security date. Do not substitute another model's blobs or flash firmware as an ordinary source update. |
| Our maintained destination forks | [Device](https://github.com/tylxr59/android_device_samsung_gta4xlveu), [kernel](https://github.com/tylxr59/android_kernel_samsung_gta4xlve), [vendor](https://github.com/tylxr59/android_vendor_samsung_gta4xlveu) | Device `fix/los24-performance-followup`, kernel/vendor `fix/los24-hardening`; exact release SHAs come from manifests, not moving branch tips. |

For USB-related updates, inspect the manifest-selected
LineageOS/android_vendor_qcom_opensource_usb lineage-24.0 source as well. The
SM-P613 correction is in device init; it uses upstream QTI HAL ownership and
requires no fourth maintained fork. See [USB findings](usb-mtp-audit.md).

Use the platform manifest's selected AOSP revisions; do not independently
replace them with AOSP `main` or an arbitrary newer tag. Merged upstream changes
are the normal update inputs. Pending Gerrit changes require a specific reviewed
reason before cherry-picking. If an upstream branch disappears or is renamed,
inspect that repository's actual branches and migration history rather than
silently falling back to its default branch.

### Fetch and compare without switching working branches

Check command availability first. With authenticated GitHub CLI, these queries
identify the two main moving heads without touching the source checkout:

```sh
gh api repos/LineageOS/android/branches/lineage-24.0 --jq '.commit.sha'
gh api repos/LineageOS/android_kernel_qcom_sm8150/branches/lineage-20 --jq '.commit.sha'
```

For each device/kernel/vendor upstream in the table, use the same
`repos/OWNER/REPOSITORY/branches/BRANCH` API query, or
`git ls-remote --heads REPOSITORY_URL refs/heads/BRANCH`. Record full SHAs and
commit dates. Compare ancestry, patch equivalence and diffs: push timestamps
and the number of forks do not establish whether a fix is missing.

For the shared kernel, set `kernel_checkout` to the existing Samsung kernel
checkout, `released_kernel_sha` to the released manifest pin, and
`last_reviewed_kernel_base` to the last documented integrated Lineage commit.
Then fetch into a separate audit ref and inspect the candidate changes:

```sh
git -C "$kernel_checkout" fetch --no-tags \
  https://github.com/LineageOS/android_kernel_qcom_sm8150.git \
  refs/heads/lineage-20:refs/remotes/upstream-audit/sm8150-lineage-20
git -C "$kernel_checkout" log --oneline --right-only --cherry-pick \
  "${released_kernel_sha}...refs/remotes/upstream-audit/sm8150-lineage-20"
git -C "$kernel_checkout" diff --stat "$last_reviewed_kernel_base" \
  refs/remotes/upstream-audit/sm8150-lineage-20
git -C "$kernel_checkout" merge-tree --write-tree "$released_kernel_sha" \
  refs/remotes/upstream-audit/sm8150-lineage-20
```

Fetch changes the object store/audit ref; these commands do not check out or
merge a working branch. `merge-tree` creates a preview tree and can report
conflicts. A clean preview does not establish compilation or hardware operation.
If history is shallow, fetch the required ancestry before interpreting results;
do not mistake missing history for an unrelated or current upstream.

The [2026-10-24 source audit](source-upstream-audit.md) records the previous
published kernel base `f136eaf93d6285680e683d7827c690ecc5c28b54`. The later
published maintenance release `1792851872` integrates the 18 reviewed commits through
`285869032633b3de3c6bdefd8f3b553f988c11da`, using kernel `88b63b7aeb73`.
These are dated references, not an instruction to reuse stale heads. Refresh the comparison and record the
integrated base after each kernel maintenance release. Keep paused experimental audio branches separate.

For a platform update, save the resolved manifest before and after the reviewed
sync and compare **project revisions**, not just the manifest repository tip.
Summarize relevant framework, security, build/toolchain, kernel and device
changes and any blockers. Never sync just to answer a read-only update query.

## One-time prerequisites

Persistent private release keys and the public pin are now initialized; see
[signing operations](signing.md). Reuse/restore those keys. Before the first
public ROM release, confirm the separate owner-held key backup and
the public certificate fingerprint. Build and test the release-signed ROM plus matching recovery. Bootstrap users from
other signing identities through a tested migration or clean installation.
Clean private-key bootstrap and a subsequent same-key Updater local install
passed with credential/data persistence on 2026-10-23. The initial test-key
prototype is not an established public update channel.
See [OTA/signing](ota.md). The first signed release and live v2 feed are published. Reuse this established
identity for every subsequent release. The first advertised network OTA test
also passed, retaining the original pattern and data without wipe.

## Routine platform updates

1. Establish the released/installed baseline and inspect current manifests,
   repository status, build environment, free storage and validation records.
   Preserve the previous release assets and target files. Reuse the existing
   Android checkout and outputs. Preserve dirty work and experimental branches
   before any sync; a clean but unreleased branch is still work to preserve.
2. Perform the source checks above and record the exact candidate upstream
   SHAs. Review platform, shared kernel and device-specific changes separately.
   Keep unrelated experiments outside the maintenance candidate.
3. Sync the LOS24 platform with the **released** fork pins still in place:
   `tools/sync-source upstream lineage-24.0`, inside the configured build
   environment with `LOS24_WORKSPACE` set to the actual workspace. The helper
   copies this public repository's fork manifest and then syncs; it is a mutating
   command. Do not run it blindly over active work branches. Capture the resolved
   platform manifest and compare it with the previous release's project pins.
4. Create candidate branches from released device/kernel/vendor commits and
   integrate only reviewed changes. Preserve the four demonstrated boot fixes,
   Gatekeeper storage policy, signing identity, OTA configuration and tested
   tablet settings. Check shared Lineage kernel fixes even when Sevenrock's
   Samsung fork has not moved. Review proprietary blob changes separately.
5. Commit candidate source changes and make their exact revisions available in
   the owner's source forks. Stage the candidate fork pins in the workspace
   local manifest and capture `repo manifest -r` before building. Another call
   to `tools/sync-source upstream` copies the public fork manifest again: do not
   let it replace candidate pins with old release pins. Keep the public resolved
   manifest identifying the validated release until the candidate is validated.
6. Build ROM/recovery, fix demonstrated failures, and retain the exact source
   manifest and target files. Sign with the existing private release identity,
   then generate the full OTA and matching recovery/vbmeta artifacts. Never
   create fresh keys as part of a routine update.
7. Verify device/version/timestamp metadata, signatures, certificate continuity,
   ZIP/AVB/VINTF results and checksums. Test recovery installation, Android boot,
   encrypted-data/pattern persistence, enforcing SELinux and the hardware smoke
   matrix. Keep rooted debugging off after checks and remove temporary probes.
   Distinguish compilation, local install and real public OTA evidence.
8. Update CHANGES.md with implementation commit links, release notes, validation
   records and source manifests to the tested
   revisions. Record the checked upstream SHAs, integrated common-kernel base,
   exclusions and reasons so the next agent does not repeat discovery. Include
   the ROM, recovery.img, correctly packaged vbmeta.img, recovery.tar,
   SHA256SUMS and source-manifest.xml. Verify padding for the 64KiB vbmeta
   partition against target-files before producing a Heimdall asset.
9. Generate feed metadata with tools/ota.py and dry-run tools/publish-update.
   If shipping/pushing an update was requested, publish validated assets and
   **then** push the feed and matching public manifests. Confirm the public raw
   endpoint and download URLs. Do not advertise an untested or nonexistent OTA.
10. Verify the previous same-key release detects, downloads, verifies, installs
    and boots the update through Android Updater. Record actual results and
    pending tests. Stop temporary host services/inhibitors and report the release
    URL, exact sources and material limitations.

Use full packages initially; incremental packages and seamless A/B updates are
not part of this device’s supported pipeline. Never perform a factory reset for
an ordinary update just to hide an upgrade defect.

## New major LineageOS releases

A new LineageOS branch is a porting task, not an automatic branch-name bump.
Review the upstream release notes, Android compatibility/FCM and kernel needs,
vendor ABI/APEX/VNDK changes, recovery/OTA format, encryption, and signing
migration. Start from our maintained device/kernel fixes, pin the new platform
manifest, attempt a baseline, then fix demonstrated build/runtime problems.
Keep the previous release available and do not advertise a new major version
in the existing feed until its upgrade path is tested. Version/API guards in
tools/ota.py must be deliberately updated with tests and migration instructions.


## Previous source audit

See [the 2026-10-24 audit](source-upstream-audit.md) for the first recorded
fork/base comparison. Use the source map above for every new check and update
its branch names if an actual upstream migration changes them.
