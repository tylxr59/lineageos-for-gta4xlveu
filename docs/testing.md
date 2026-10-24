# Test status

Current release: [lineage-24.0-20261023-gta4xlveu-1792787032](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792787032), with device `eb9bc69`, kernel `75a416868` and vendor
`4388d72`. Public HTTPS OTA, data persistence, security checks and the released
recovery round trip passed. Owner Wi-Fi/camera/speaker/S Pen smoke and lock-icon
visual checks passed on the same-source signed build; executable/package
contents match the published build. See the [follow-up evidence](#wi-fi-tablet-and-lock-icon-follow-up)
for exact results and remaining untested hardware cases.

## Initial port validation

The owner’s SM-P613 booted the ordinary logger-free LOS24/Android17 build on
2026-10-23. Sources: device `44bda91`, kernel `75a416868`, unchanged vendor
`4388d72`; exact snapshot: [known-good.xml](../manifests/known-good.xml).

| Check | Evidence/status |
| --- | --- |
| Compilation | Full ROM and recovery passed; ordinary incremental build 7m31s |
| Recovery | Source-built Lineage Recovery 24 boots; ADB/sideload work |
| Ordinary system boot | Android setup completed; subsequent same-key update booted |
| Data | FBE encrypted; mapped userdata mounted; setup/settings survived update |
| SELinux | Enforcing in Android |
| Keymaster / Keystore | Services registered after permission-rule fix |
| ADB | Normal and opt-in root tested; rooted debugging disabled afterward |
| USB / charging | USB HALs registered, charging reported |
| MTP | MTP+ADB functions/re-enumeration checked; file transfer untested |
| Wi-Fi | Owner smoke test passed |
| Front/rear cameras | Owner smoke test passed |
| Speakers | Owner playback smoke test passed |
| S Pen | Owner writing/hover smoke test passed; pressure-level accuracy untested |
| Crash buffer | Empty after ordinary build boot; not an endurance test |
| Bluetooth audio | Untested |
| Deep suspend / battery endurance | Initial overnight confounded by background media; controlled baseline pending ([audit](battery-audit.md)) |
| microSD | Untested |
| Credential-protected encryption after update/reboot | Original pattern unlock and saved-file checksum passed on corrected signed build |
| OTA endpoint / v2 feed fetch | OTA-enabled build installed; owner confirms Updater refresh succeeds |
| Private signing | Candidate verified: 126 standalone + 28 nested APKs, 38 APEXes, OTA/recovery/AVB |
| Private-key hardware bootstrap | Clean install and Android boot passed |
| Same-key Android Updater local install | Corrected signed build installed and booted; original pattern/setup/test data retained |
| Advertised public OTA download/install | Passed: live feed → GitHub download → signature verification → recovery install → boot; original pattern/data/setup retained |

Manual sideload updates were installed with recovery status 0 and full boot/DTBO
readback matching OTA images. ZIP CRC, OTA certificate continuity, AVB image
verification, and actual system/vendor filesystem content were checked. The
installed imported vbmeta configuration uses flags 3; the device tree also
retains a VINTF kernel-requirements bypass. Those are inherited limitations,
not proof of verified-boot security or complete Android17/kernel compatibility.

The prototype is signed with public development keys. Its OTA SHA-256 is
`21d9fd0f505ff93b8cd8b418b719dbcb1eefcdece66853490a69bb433e2de90a`.
No prototype binary is offered as a public release.

The earlier OTA-enabled follow-up (device `d4723ed`, same kernel/vendor)
compiled successfully in 5m09s.
It passed ZIP/certificate continuity checks; OTA boot/DTBO match the preceding
working package byte for byte, and its actual product filesystem contains the
correct endpoint. It was installed by recovery sideload-auto-reboot without
wiping. The subsequent Android boot reports its unique new timestamp and URL,
boot complete, encrypted data, enforcing SELinux, normal ADB UID2000, and an
empty crash buffer. Rooted debugging stays off. The owner confirmed the live
Updater refresh succeeds with the empty v2 feed. This does not establish a
public release-signed OTA download/install or a key-migration procedure.
Follow-up OTA SHA-256:
`869cb070f474168b62d7b7a527898d65b5f924cf79f8db26afedc3cf0822aedc`.

## Private-key signing and update tests

Persistent signing keys are initialized and the OTA public certificate is pinned
in `ota/release-cert.sha256`. APK/container signatures, APEX public-key/payload
signatures, nested APKs, actual recovery ramdisk OTA trust, AVB signatures and
Android whole-file OTA signatures passed. The prescribed presigned CTS self-test
shim is retained. Twenty local tooling tests pass.

The first private-key recovery refused its OTA because mapped extra keys created
duplicate ZIP names in `otacerts.zip`. The owner cancelled that installation.
The wrapper now deduplicates mapped extra keys and the verifier rejects such
archives. The regenerated recovery and matching vbmeta booted, with full image
readback and its live single-certificate trust archive checked. The corrected
OTA then passed recovery's real signature check and installed with status 0.
Its boot/DTBO/recovery/vbmeta partition hashes matched the signed bundle.

The clean private-key Android installation completed setup and reported
release-keys, FBE, SELinux enforcing, normal ADB UID2000, rooted debugging off,
and an empty crash buffer. Its installed Updater APK matched the private platform
certificate. Android Updater imported and verified a newer same-key full OTA,
then rebooted to recovery and installed it without a format. The new build
returned with timestamp `1792773624` and setup flags intact.

The first credential-protected reboot exposed a Gatekeeper policy defect: the
correct pattern was rejected and user 0 stayed `RUNNING_LOCKED`. QSEECom in the
`tee` domain could not access `gatekeeper_vendor_data_file`. Device `4c68bc9`
moved the two existing narrow allow rules out of the unincluded private policy
directory into the active vendor policy. Neverallow checks passed; the compiled
policy delta contains exactly those two added allow rules. SELinux stayed
enforcing and no credentials or data were removed.

The repair installed with the same keys and no wipe, passed recovery signature
verification/status 0, and booted at timestamp `1792775285`. The owner's original
pattern unlocked it; the original saved-file checksum matched and Gatekeeper
AVCs disappeared. A subsequent same-source, newer signed build then imported,
verified and installed through Android Updater's local-update path. It booted at
`1792775790`, unlocked with that same pattern, and retained setup and the saved
file. Android reports FBE, enforcing SELinux, normal shell UID2000, disabled
Rooted debugging and an empty crash buffer. The owner repeated Wi-Fi, both
cameras, speakers and S Pen smoke checks successfully.

First signed release source: device `4c68bc975d304483675ceab24e75c31ab2d2c515`, kernel
`75a416868f994657bb1095f9e76864525c184f84`, vendor
`4388d72aed64812cf27496986bcf8fb3af64bf1d`. Its exact snapshot is attached as
[source-manifest.xml](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/download/lineage-24.0-20261023-gta4xlveu-1792775790/source-manifest.xml). The follow-up vendor policy is byte-
identical to the successful repair. Final tested ROM SHA-256:
`3f6464a2673b86a23aaf690fa3789d007b122f5f521a420af6f60042f0cb8c8c`.
Matching candidate recovery SHA-256:
`da434b6e7b8dd095a88f86daff568b057b5d38fd17496d7c3ff61a7d1e4e2767`.
The exact final recovery and padded vbmeta were transferred together through
the documented Heimdall command. Recovery booted; full partition hashes and its
live single-certificate OTA trust matched the release assets. The earlier
same-key recovery performed the preceding local update test.

The first signed release and v2 feed entry are now published. Public asset sizes
and GitHub SHA-256 digests match the local bundle; the downloaded public checksum
file matches. Android Updater on the prior same-source build detected the newer
release, downloaded it from GitHub, and verified the package using the installed
OTA trust. The normal Install confirmation rebooted into the exact released
recovery, installed the package, and returned to Android at timestamp1792775790.
The owner unlocked with the original pattern and confirmed setup intact. The
original saved-file SHA-256 matched, user 0 was RUNNING_UNLOCKED, FBE and SELinux
enforcing remained active, normal ADB UID2000 and disabled Rooted debugging were
verified, and the crash buffer was empty with no Gatekeeper AVCs. No factory
reset was used. Temporary test files/local-import entry were removed and the
original screen-awake setting restored. This is an actual advertised network
OTA test, in addition to the earlier local-import test.

Published release: [lineage-24.0-20261023-gta4xlveu-1792775790](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792775790). Bluetooth audio, microSD, deep suspend/battery endurance, MTP file transfer,
and S Pen pressure accuracy remain untested.

## Wi-Fi tablet and lock-icon follow-up

Device `eb9bc69ee6b6750f66258a55535fa41ff008541a` adds the Wi-Fi-only tablet
configuration and SystemUI padding overlay. Kernel/vendor/platform revisions
are unchanged. All 1,242 revisions match the current [resolved manifest](../manifests/resolved.xml).

The product reconfiguration required broad SDK/app rebuilds. Earlier attempts
were stopped by the host's memory-pressure manager. Resuming cached work with
four compile jobs and verified Go runtime budgeting completed target files in
17m34s. This is an incremental recovery time, not a clean-build benchmark.

Signed local-test build `1792785825` passed recovery sideload and Android boot
without a wipe. Actual signed target-file content confirms tablet characteristics,
no bundled Phone/Contacts/Messaging/SIM Toolkit APKs, no unconditional IMS feature,
and a matching embedded recovery image. Android retains the contacts provider
and picker needed by other apps; these are separate from the removed launcher app.
Verification passed for 120 standalone APKs, 37 APEX containers/payloads and 26
nested APKs, the single-certificate recovery trust, AVB and the whole-file OTA
signature, using the existing persistent signing identity.

Runtime reports `ro.build.characteristics=tablet`, no telephony feature, and
voice/SMS/mobile-data capability resources set to false. Lock-icon padding
resolves to `24.0dip`: 36px per side at the unchanged native 240dpi, leaving a
36px foreground within the unchanged 108px target. The owner confirmed the icon
looks normal. The original pattern, setup and saved-file checksum survived;
FBE, SELinux enforcing, normal shell UID2000, Rooted debugging disabled and an
empty crash buffer passed. Owner Wi-Fi, both cameras, speakers and S Pen smoke
tests passed again.

The newer same-source build `1792787032` is the [published follow-up](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792787032).
Comparison of 3,779 executable/package entries finds only the expected recovery
installer's image-digest change; all APK/APEX/native-library and remaining binary
entries, boot/DTBO images and vendor policy match the locally tested build.

All 12 public asset sizes/digests and the downloaded checksum file matched.
The installed previous same-key test build detected the new entry through the
canonical HTTPS feed, downloaded the GitHub asset, completed signature
verification, and installed it through Updater's normal recovery flow. Android
booted at1792787032 without a wipe. Encrypted data unlocked, the saved-file
checksum and setup flags persisted, SELinux was enforcing, ADB UID2000 and
Rooted debugging off passed, and the crash buffer was empty with no observed
Gatekeeper data AVCs. A further recovery/Android round trip repeated the data
and security checks.

Automatic recovery updating also passed: the exact released recovery booted at
1792787032, and full boot/DTBO/recovery partition readback matched the release
assets. Its live trust archive contains exactly the pinned OTA certificate.
Ordinary OTA retained the preceding vbmeta partition
(`95bafe991ff7875da220522abd1b916d92ba563eaff42447e3eac8d01be80f10`), with the
inherited flags3 configuration. The new matching vbmeta asset was validated on
the host; it was not manually flashed for this routine update.

ROM SHA-256: `7947f4ddff96e85dc5772a7a7a30474d430b55af2938e2223b7781634bd278d3`.
Recovery SHA-256: `856aa83f9cba5f113b25a04f72a6d95ca7703b4058e8a00e9957c471a5cf22a8`.
The same 47 private signing identities and owner-held encrypted backup were
retained. Initial tablet feed checks received GitHub's cached old feed; after
cache revalidation the regular Updater refresh detected the new build. No ROM
or endpoint change was needed.

The Clock home widget's one-row text size remains constrained by its height;
increasing widget height is the proposed layout workaround. The launcher layout
and global density/font scale were not changed. Bluetooth audio, microSD, deep
suspend/battery endurance, MTP file transfer and S Pen pressure accuracy remain
outside the completed smoke matrix.
