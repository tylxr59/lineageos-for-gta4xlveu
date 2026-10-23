# Test status

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
| Deep suspend / battery endurance | Untested |
| microSD | Untested |
| Credential-protected encryption after lock/reboot | Untested |
| OTA endpoint / v2 feed fetch | OTA-enabled build installed; owner confirms Updater refresh succeeds |
| Private signing | Candidate verified: 126 standalone + 28 nested APKs, 38 APEXes, OTA/recovery/AVB |
| Private-key hardware bootstrap / advertised OTA install | Not yet tested |

Manual sideload updates were installed with recovery status 0 and full boot/DTBO
readback matching OTA images. ZIP CRC, OTA certificate continuity, AVB image
verification, and actual system/vendor filesystem content were checked. The
installed imported vbmeta configuration uses flags 3; the device tree also
retains a VINTF kernel-requirements bypass. Those are inherited limitations,
not proof of verified-boot security or complete Android17/kernel compatibility.

The prototype is signed with public development keys. Its OTA SHA-256 is
`21d9fd0f505ff93b8cd8b418b719dbcb1eefcdece66853490a69bb433e2de90a`.
No prototype binary is offered as a public release.

The OTA-enabled follow-up (device `d4723ed`, same kernel/vendor), pinned in
[resolved.xml](../manifests/resolved.xml), compiled successfully in 5m09s.
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

## Private-key candidate verification

Persistent signing keys are initialized and the OTA public certificate is pinned
in `ota/release-cert.sha256`. The signed candidate and matching recovery/vbmeta
assets passed APK/container signatures, APEX public-key/payload signatures,
nested APK signatures, actual recovery ramdisk OTA trust, root AVB signatures,
and Android whole-file OTA CMS signature verification. The prescribed presigned
CTS self-test shim is retained. The release publisher dry-run passed; 17 local
tooling tests pass, including tamper rejection and key-loss/permission guards.

These checks are offline evidence. The tablet still runs the working development-
key installation. No first private-key boot, cross-key migration, or subsequent
same-key OTA has been claimed, and the live public feed remains empty.
