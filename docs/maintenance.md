# Updating upstream and shipping a release

The intended operator workflow is a request such as **“get us up to date with
mainline LineageOS and push an update.”** An agent should carry that request
through publication once the following evidence is in place. Source compilation
alone is not a release success criterion.

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
identity for every subsequent release.

## Routine platform updates

1. Inspect the current manifests, build environment, free storage, repository
   status, and prior test/release record. Preserve the previous release assets
   and target files. Reuse the existing Android checkout and outputs.
2. Fetch upstream LineageOS changes. For LOS24 platform updates, use the official
   `lineage-24.0` branch with our pinned device/kernel/vendor local manifest:
   `tools/sync-source upstream lineage-24.0` in the build environment. Review
   sync changes and capture `repo manifest -r` before building. Do not discard
   uncommitted source fixes or a developer’s branch.
3. Review device/kernel upstream changes separately and merge useful fixes onto
   maintained branches, preserving the four demonstrated boot fixes and the Gatekeeper policy fix. Do not
   auto-replace forks with upstream just because a branch has a newer timestamp.
4. Build the ROM/recovery, fix demonstrated failures, and record all source
   revisions. Sign target files with the existing release identity, then generate
   the full OTA and matching recovery/vbmeta artifacts. Never create fresh keys
   as part of a routine update.
5. Check metadata/device/version/timestamp, signatures, certificate continuity,
   ZIP/AVB/VINTF results and checksums. Test recovery installation, Android boot,
   encrypted-data persistence, SELinux enforcing, and the feature smoke matrix.
   Keep ordinary rooted debugging off, no temporary logging or app-root tools.
6. Prepare release notes describing actual changes and known issues. Include the
   ROM, recovery.img, correctly packaged vbmeta.img, recovery.tar, SHA256SUMS and
   source-manifest.xml. For this 64KiB vbmeta partition, image padding must be
   explicitly checked against target-files before producing a Heimdall asset.
7. Generate candidate feed metadata with tools/ota.py. Dry-run tools/publish-update.
   If the user requested shipping/pushing an update, publish release assets and
   **then** push the feed. Confirm the public raw endpoint and download URLs.
8. Verify the installed previous same-key release detects, downloads, verifies,
   installs and boots the update from Android Updater. Record the result and
   pending hardware tests. Stop temporary host services/inhibitors. Report the
   release URL, exact source snapshot and evidence/limitations.

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
