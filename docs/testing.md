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
| Public release keys / automatic OTA | Not yet tested |

Manual sideload updates were installed with recovery status 0 and full boot/DTBO
readback matching OTA images. ZIP CRC, OTA certificate continuity, AVB image
verification, and actual system/vendor filesystem content were checked. The
installed imported vbmeta configuration uses flags 3; the device tree also
retains a VINTF kernel-requirements bypass. Those are inherited limitations,
not proof of verified-boot security or complete Android17/kernel compatibility.

The prototype is signed with public development keys. Its OTA SHA-256 is
`21d9fd0f505ff93b8cd8b418b719dbcb1eefcdece66853490a69bb433e2de90a`.
No prototype binary is offered as a public release. The newer candidate adds
the maintained OTA endpoint; update this table only after its own checks pass.
