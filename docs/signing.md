# Release signing operations

## Established identity

The persistent signing identity was created on 2026-10-23. The public OTA
certificate pin is [ota/release-cert.sha256](../ota/release-cert.sha256):

`4d4cac9bcb4287bf5e9d10be5e6a41f8c92e86e01c1b577587700d986fd4845e`

The current key inventory has 47 RSA-4096 identities: eight app/OTA keys,
38 APEX container/payload identities, and a separate AVB key. APK privilege
relationships use the platform/shared/media/networkstack/etc. identities;
additional module APK certificates map to releasekey. The upstream presigned
CTS self-test shim is intentionally retained, as required by its self-tests.
The recovery trusts only our OTA identity. AVB flags remain 3 as in the tested
device configuration; changing signing keys does not enable locked verified boot.

Private keys are **not in this repository**. On the existing build workspace,
they are under ignored `keys/gta4xlveu-release/`, mode 0700 with mode-0600 files.
Working PEM/PKCS#8 keys support unattended local signing; the export backup is
AES-256 encrypted with a separately stored random passphrase. Never place the
private keys or that passphrase in a public release, repository or CI secret log.

An encrypted backup passed a decrypt/byte-for-byte round-trip check. A verified
copy and separate restricted passphrase file are stored outside the build
workspace in the owner’s chosen backup location. Keep an off-machine copy too;
a second directory on the build disk does not protect against disk loss. Restore
these keys on a replacement builder instead of generating a new identity.

## Reuse, restore, and future APEX additions

Use the existing inventory. The tools check the public pin and refuse missing,
partial or changed keys rather than silently replacing them. `init` is for
adding required keys for a new source inventory **after restoring the original
release identity**, not for recreating lost keys. A new clone with no private
keys and an existing public pin will refuse initialization.

Restore the encrypted tar into the workspace’s ignored keys directory using
GPG and a separately supplied passphrase, under umask 077. The archive contains
`gta4xlveu-release/`. Verify permissions and all key/certificate pairs before
signing; do not overwrite an existing directory without inspecting it.

To inventory a new target-files archive and add any newly required APEX keys:

```sh
tools/release-signing.py plan --target-files artifacts/unsigned-target-files.zip
tools/release-signing.py init --target-files artifacts/unsigned-target-files.zip \
  --keys keys/gta4xlveu-release
```

Old identities are retained for continuity and rollback. Never delete the
inventory or regenerate keys to resolve a signing-tool error.

## Sign and verify a build

Run in the configured Linux build environment. Paths below assume the public
project is the workspace root; for the existing nested checkout, invoke its
scripts from the parent workspace using the existing Ubuntu wrapper.

```sh
# In Android: build target-files-package and otatools first.
tools/release-signing.py sign \
  --target-files artifacts/unsigned-target-files.zip \
  --keys keys/gta4xlveu-release --android android \
  --output artifacts/signed-target-files.zip

# In the Android build environment, with otatools and Java on PATH:
ota_from_target_files -p android/out/host/linux-x86 \
  -k keys/gta4xlveu-release/releasekey --block --backup=true \
  artifacts/signed-target-files.zip \
  artifacts/lineage-24.0-YYYYMMDD-UNOFFICIAL-gta4xlveu.zip

tools/verify-release.py --target-files artifacts/signed-target-files.zip \
  --keys keys/gta4xlveu-release --android android \
  --work-dir artifacts/verification --output artifacts/component-verification.json

tools/verify-ota artifacts/lineage-24.0-YYYYMMDD-UNOFFICIAL-gta4xlveu.zip \
  --cert keys/gta4xlveu-release/releasekey.x509.pem \
  --work-dir artifacts/verification
```

The signer calls this Android branch’s `sign_target_files_apks`, replaces OTA
trust, re-signs APK/APEX keys, substitutes private recovery/vbmeta AVB keys, and
changes build tags to release-keys. The verifier checks actual APK/container and
APEX payload signatures, nested APKs, OTA trust archives, the actual recovery
ramdisk and AVB signatures. OTA trust ZIPs must also contain unique entry names; recovery
rejects duplicate names even when every certificate fingerprint matches. The
wrapper deduplicates mapped extra keys before signing. `verify-ota` verifies Android’s detached CMS whole-file
signature against the pinned self-signed identity. It skips public-CA chain
validation, never cryptographic content/signature verification. The publisher
runs this whole-file check before offering its dry-run or publishing.

Extract recovery/boot/DTBO/vbmeta from the **signed** target files and compare
boot/DTBO to the actual signed OTA. Pad the signed vbmeta to the tested 65,536
byte partition size without changing its signed bytes, then make recovery.tar
from the matching recovery.img and padded vbmeta.img. Include the exact source
manifest, public release certificate and checksums. Never distribute private
PEM/PKCS#8 files or unsigned/mismatched recovery assets.

## Backup

```sh
tools/release-signing.py backup --keys keys/gta4xlveu-release \
  --output artifacts/key-backup-UNIQUE-DATE
```

The tool refuses an existing backup output, uses the separately stored
`keys/gta4xlveu-backup-passphrase.txt`, and verifies decryption before reporting
success. Back up again after adding any identities. Save the encrypted export
and its passphrase separately in owner-controlled storage.

## First installation

The private-key candidate is an **unofficial release-key build**, not an official
LineageOS build. Offline signature checks do not establish hardware boot or an
in-place migration. Development-key builds have a different system app/APEX identity. Before advertising an OTA to public users, test a one-time
clean installation or a separately reviewed key migration, using the matching
signed recovery, and then a subsequent same-key update. Do not silently wipe
userdata as part of a routine update or treat the first key transition as an
ordinary OTA. Only advertise an authorized, tested release on the live feed.

The 2026-10-23 bootstrap and subsequent same-key Android Updater local install
passed on SM-P613 after the Gatekeeper-policy fix. The original pattern, setup
and saved data survived. This verifies the clean bootstrap/local installation
path. The first public release and its feed entry are now published; the
HTTPS download/install test is recorded separately in docs/testing.md.
