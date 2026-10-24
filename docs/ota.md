# OTA channel and release signing

## Architecture and current state

Danielml3 hosts ROM assets on [GitHub Releases](https://github.com/danielml3/releases)
and publishes a [v2 static feed](https://github.com/danielml3/releases/blob/main/v2_lineage_gta4xlveu.json).
We use the same model, without a paid service or a separate update server:

- Feed: `https://raw.githubusercontent.com/tylxr59/lineageos-for-gta4xlveu/main/ota/gta4xlveu.json`
- ROM property: `lineage.updater.uri` in the device’s product properties.
- Assets: this repository’s GitHub Releases, published before feed updates.
- Format: a JSON **array** matching LOS24’s `NetworkUpdate` / `NetworkUpdateFile`.
  The old `{ "response": [...] }` API is not accepted by this client.
- Device: non-A/B, full block OTA. Updater downloads/verifies and recovery installs.

Source references: [Updater network parser](https://github.com/LineageOS/android_packages_apps_Updater/blob/lineage-24.0/app/src/main/java/org/lineageos/updater/data/source/network/NetworkUpdate.kt)
and [endpoint selection](https://github.com/LineageOS/android_packages_apps_Updater/blob/lineage-24.0/app/src/main/java/org/lineageos/updater/data/source/network/UpdatesNetworkDataSource.kt).
The client requires HTTPS and does not follow redirects for the feed, so use the
raw URL directly. An empty `[]` is a valid no-updates response.

[The first signed release](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792775790) and its v2 feed entry are published.
All 12 release assets were uploaded before the feed commit. Public checksum
contents match the local bundle; asset byte sizes and GitHub's SHA-256 digests
match. Exact release recovery/vbmeta flashing, recovery boot, full image readback
and live OTA trust passed. Private-key clean bootstrap and corrected same-key
local Updater installation retained the original credential/setup/test data.
The advertised HTTPS Updater path also passed: the prior identical-source,
same-key build detected and downloaded the public release, verified its signature,
installed through recovery and rebooted. The original pattern/setup/test file
survived without wipe, with encrypted storage and SELinux enforcing.
Persistent keys and their public pin remain unchanged; see [signing operations](signing.md).

## Persistent signing identity

Follow [LineageOS signing builds](https://wiki.lineageos.org/signing_builds).
Read the signing tools from the checked-out Android branch before running them;
Android major releases can change APK/APEX payload/container keys and options.

1. Generate the complete APK, OTA, AVB and APEX key set required by this target’s
   `META/apkcerts.txt`, `META/apexkeys.txt` and signing configuration. Use private
   storage such as ignored `keys/` with restrictive permissions. Back it up to a
   separate owner-controlled location. Do not print private material or place it
   in Git, GitHub artifacts, issue reports, release bundles or CI logs.
2. Use `sign_target_files_apks` on the unsigned target-files ZIP, with the private
   APK/APEX/AVB mappings. Retain the signed target files for future reproductions.
   Supplying only an OTA releasekey does not replace the platform/APEX identities.
3. Generate the full non-A/B ZIP using `ota_from_target_files -k ...` with the
   persistent OTA key. Extract the matching recovery and images from the signed
   target files. Check the signed recovery trusts the OTA key. Do not mix a
   test-key recovery/vbmeta tar with a newly signed public ROM.
4. Verify the package’s whole-file signature against the public certificate;
   certificate comparison alone is not signature verification. Boot/install it
   using the matching recovery and verify encrypted data and enforcing SELinux.
5. Commit only the OTA public certificate’s SHA-256 DER fingerprint as
   `ota/release-cert.sha256` (one lowercase hex line). Example:

   ```sh
   openssl x509 -in keys/releasekey.x509.pem -outform DER | sha256sum
   ```

Do this once, before public users establish a signing identity. Never rotate the
keys as part of an ordinary platform update. Transitioning the local prototype
or another maintainer’s builds requires separately tested key migration or a
clean installation. Do not promise data preservation across different identities.

## Prepare metadata locally

After signing and validation, choose a unique immutable release tag and run:

```sh
tools/ota.py prepare artifacts/release/lineage-24.0-YYYYMMDD-UNOFFICIAL-gta4xlveu.zip \
  --tag lineage-24.0-YYYYMMDD-gta4xlveu-TIMESTAMP \
  --output artifacts/release/candidate-feed.json
tools/ota.py validate artifacts/release/candidate-feed.json
```

The tool reads device, build timestamp, SDK, patch level and metadata ranges
from the ZIP, verifies the ranges against the actual stored entries, computes
SHA-256/byte size, checks the pinned certificate and rejects development-key
build tags, then prepends a new v2 entry. It writes a **candidate**, not the live
feed. The timestamp is the ROM’s `post-timestamp`, never the upload time.

`tools/ota.py` does not sign packages or verify their whole-file cryptographic
signature. Run `tools/verify-ota`; the publisher now performs that check too.
Recovery installation/boot checks remain required. The initial known test-key
ROM is refused.

## Publish an authorized release

Prepare a release directory with the ROM, matching recovery.img, padded
vbmeta.img, recovery.tar, exact source-manifest.xml and SHA256SUMS covering all
assets except the checksum file itself. Release notes must state upgrade
requirements, signing identity, tests, changes and remaining limitations.

```sh
tools/publish-update \
  --rom artifacts/release/lineage-24.0-YYYYMMDD-UNOFFICIAL-gta4xlveu.zip \
  --candidate-feed artifacts/release/candidate-feed.json \
  --notes artifacts/release/notes.md \
  --asset artifacts/release/recovery.img \
  --asset artifacts/release/vbmeta.img \
  --asset artifacts/release/recovery.tar \
  --asset artifacts/release/SHA256SUMS \
  --asset artifacts/release/source-manifest.xml
```

This is a dry-run. Add `--execute` only for an owner-authorized release with
completed signing/install checks. It checks local hashes and metadata, requires
clean main matching origin/main, creates/uploads the GitHub release, then
commits/pushes the feed. If upload fails, it does not change the feed. If feed
push fails after release creation, reconcile the branch and publish the feed;
do not delete/recreate a release or force-push blindly. The script deliberately
has no unattended GitHub Actions deployment or embedded signing credentials.

Finally verify raw feed HTTP 200, checksums and downloadable assets, then test
refresh/download/install on the prior same-key build. Public HTTPS reachability
alone is not evidence of successful recovery installation.


GitHub's raw-file CDN can cache the feed for five minutes after publication.
If a refresh still shows the preceding feed, compare the canonical endpoint
from the tablet's network and allow for cache expiry or HTTP revalidation.
A successful refresh with an older cached feed is separate from package
signature/installation failure; do not rebuild or change signing keys for it.


## Current maintenance release

[Build 1792851872](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792851872) is published with the same persistent signing identity.
All 12 assets were uploaded before the feed, and public asset sizes/digests,
downloaded checksums and the canonical HTTPS feed were verified. Signed local
installation, recovery partition readback and Android/data/security tests passed.
The tablet already ran this timestamp at publication, so no separate older-to-newer
public Updater installation is claimed for this build. See [testing](testing.md).

A fresh download of the public ROM ZIP matched the tested bundle SHA256. The
tablet also fetched the canonical three-entry HTTPS feed successfully.
