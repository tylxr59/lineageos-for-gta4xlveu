# USB file transfer investigation (2026-10-24)

The owner reported File Transfer reverting to No data transfer before the
hardening update. The issue was reproduced on signed candidate1792860066 using
the same computer/cable as ADB and KDE Dolphin. The public1792851872 release has
not received this correction.

## Demonstrated cause

MtpService starts with unlocked storage. The QTI gadget HAL then fails to link
its ADB function with EEXIST, reports ERROR to UsbDeviceManager, and Android
falls back to charging before the host MTP client can use the connection.

The device's init.target.rc **on boot** action selects sys.usb.configfs=1 even
though the product enables the QTI AIDL gadget HAL. The imported QTI USB init
selects mode2 for HAL ownership, but this later device action overwrites it.
Mode1 also enables legacy init function handlers. The live gadget consequently
had both legacy f1 and HAL function0 links to ffs.adb. The HAL reset helper removes
its functionN links, leaving the legacy link behind; MTP+ADB setup collides with
that remaining binding.

During a later debugging restart failure the host descriptors showed two ADB
interfaces. A debugging toggle reduced this to one and restored ADB. This is a
plausible explanation for the reconnect trouble as well as the demonstrated
MTP failure; long-term reconnect reliability still needs testing.

## Live diagnostic evidence

A temporary privileged test selected HAL ownership and removed legacy links.
MTP+ADB then remained selected with function0=ffs.mtp and function1=ffs.adb.
KDE KIO wrote a known probe to the tablet and read it back, with matching
host/tablet SHA256. The owner independently browsed internal storage and
transferred a file through Dolphin.

No persistent USB preference was changed. The diagnostic process ended during
USB re-enumeration before its cleanup ran, so saved volatile properties were
restored explicitly and verified. Do not rely on an ordinary adbd child for
rollback across USB reconfiguration. Temporary scripts/logs/helper were removed.
Rooted debugging was disabled through the official service; normal UID2000 and
disabled state were verified after reconnect. The owned MTP probe is retained
for the candidate update/data-persistence check.

## Permanent source correction

Device commit02b4ef7 selects configfs=2 in its normal on boot action. Its separate
charger-only legacy configuration remains unchanged. The existing QTI gadget
HAL owns normal USB function setup, matching its upstream init contract. Kernel,
SELinux and shared USB sources are unchanged. This requires no additional source
fork beyond the existing device/kernel/vendor forks.

This selects the owner, rather than forcing File Transfer to be enabled.
Android continues to apply the user's lock, debugging and data-transfer choices.

## Source-built candidate validation

Signed candidate **1792876959** uses device02b4ef7, kernel0c5ccf4fc and
vendor1c0a6f2. Compilation, strict VINTF, enforcing CFI/KPTI, final-image checks,
APK/APEX/AVB signatures, single recovery trust certificate and whole-OTA signature
verification passed with the existing release certificate. Kernel, DTBO, compiled
policy and shared USB init are byte-identical to the tested hardening candidate.
All1,242 project pins match that candidate except device; see the
[candidate manifest](../manifests/candidates/usb-mtp-20261024.xml).

The signed no-wipe update booted Android. Data unlocked and the pre-update saved
file checksum matched. File encryption, enforcing SELinux, normal ADB UID2000,
Rooted debugging disabled, actual kernel/config identity and empty crash buffer
passed. Automatic recovery payload/updater target matches the signed recovery;
a fresh recovery boot/full partition readback is still pending.

Fresh Android boot selected configfs2 without runtime root changes. Five USB mode
selections (MTP, charging, MTP, charging, MTP) passed. Every host descriptor check
showed exactly one ADB interface; MTP modes also showed one MTP interface. ADB
reconnected without restarting its host service or toggling debugging. MTP held
beyond the previous failure window. KDE KIO wrote and read a new probe with
matching host/tablet SHA256. The issuing shell can disconnect during USB function
changes, so tests check actual reattachment/functions rather than interpreting
that shell's transport exit as the function-switch result.

Owner physical reconnect/Dolphin and pattern/setup confirmation, matching
recovery and final cleanup are pending. These repeated mode-switch tests support
both symptoms being corrected; they do not establish long-term USB reliability.
No ROM release or OTA feed change has occurred. The public release remains
1792851872; do not point its manifests at this unreleased candidate.
