# Port findings

The [speaker audio audit](audio-audit.md) records the current vendor calibration,
TI amplifier route, AudioFX capabilities, unresolved ACDB table errors and the
checks required before audio tuning. It made no changes to tablet audio settings.

The pinned Sevenrock LOS24 baseline compiled unchanged, but compilation did not
establish bootability. Initial boot testing on SM-P613 found four independent defects.

| Defect | Evidence | Fix |
| --- | --- | --- |
| Missing recovery init | New ramdisk lacked init.recovery.qcom.rc; init could not establish bootdevice/cache paths or USB/backlight setup | Device `e44d4d7`: explicitly copy recovery/root/init.recovery.qcom.rc with PRODUCT_COPY_FILES; remove unused TARGET_RECOVERY_DEVICE_DIRS |
| Removed reserved memory | Baseline recovery returned to Download Mode; replacing only DTB with the installed known-good DTB booted the new kernel/recovery | Kernel `75a416868`: restore five-line disp_rdump_region@9c000000 node and symbol in atoll.dtsi |
| Obsolete ueventd path | init reached storage, but QSEECom/ION nodes had restrictive default permissions and Keymaster could not register | Device `78014df`: install rules at vendor/etc/ueventd.rc, imported by Android17, instead of vendor/ueventd.rc |
| Missing USB controller | QTI gadget HAL exited “UDC name not defined”; system_server watchdog stack waited in UsbService boot phase, causing repeated animation | Device `44bda91`: vendor.usb.controller=a600000.dwc3, matching live UDC and boot command line |

The working DTB matches the original installed DTB byte for byte. This retains
the newer kernel’s clone3/TLS backports and module signing; no kernel downgrade
or global SELinux relaxation was needed. The DTB substitution establishes the
node’s practical requirement on this tablet without claiming a proven internal
bootloader failure mechanism.

A temporary userdebug cache logcat service was used to capture logs before
userdata mounted. It was removed from source and actual final system image.
No diagnostic logger should enter a public build.

The source forks preserve imported lineage-24.0 branches. Working fixes are on
device fix/los24-usb-controller and kernel fix/los24-boot-dtb; the OTA candidate
adds one product property on device fix/los24-updater. The exact known-good and
current-candidate manifests preserve all platform project revisions separately.

During testing, plain `adb reboot` once returned to recovery. Recovery-menu
normal reboot uses `sys.powerctl=reboot,userrequested,recovery`; with the BCB
command clear, that route consistently booted Android. Read actual state before
using this workaround. Recovery ADB may need Advanced → Enable ADB after each
sideload. Successful adb transfer alone is insufficient: check recovery status 0.

Heimdall recovery/vbmeta transfers worked after fresh entry into the blue Samsung
Downloading screen using amo13/Heimdall commit
`8378ba4081875e220d31815ccb7e907112c16481`. Reusing a stale USB session failed
before transfer. Fastboot answered queries but rejected flash commands; it is
not the supported installation path. No PIT rewrite or bootloader firmware
flash was needed. Original partition backups and rollback resources are local.

## Release-signing trust archive

The first private-key recovery booted, but refused the matching signed OTA before
signature verification. Its log reported `Duplicate entries in archive` while
opening `otacerts.zip`, followed by `Failed to load keys`. Mapping the upstream
extra Lineage recovery key to our primary release key made releasetools write the
same ZIP filename twice. Checking certificate fingerprints alone missed this.
The install was cancelled rather than accepting the signature warning.

The signing wrapper now removes extra OTA/recovery keys that map to an already
listed primary identity before invoking releasetools. It handles the empty
`META/otakeys.txt` case, which falls back to `default_system_dev_certificate`.
The original unsigned archive and persistent keys remain unchanged. Component
verification rejects empty trust archives and duplicate ZIP entries, including
inside the actual recovery ramdisk. The regenerated image booted and accepted the signed OTA with a real recovery
whole-file signature check and installation status 0.

## Pattern unlock after reboot

The first signed same-key update installed through Android Updater and booted,
but a correct setup-created pattern was rejected after restart. This was the
first credential-protected reboot test; an update-triggered reboot exposed the
defect without establishing that the update introduced it. User 0 remained
`RUNNING_LOCKED`. QSEECom in the `tee` domain was denied read/search access to
`gatekeeper_vendor_data_file`, and Samsung Gatekeeper reported secure-failure-
record load/save errors (`-506`).

The tree already had the intended directory/file allow rules in
`sepolicy/private/tee.te`, but BoardConfig includes only the vendor and
system_ext/public policy directories. Device `4c68bc9` moves these existing
narrow rules to `sepolicy/vendor/tee.te`. The real build/neverallow checks passed. A no-wipe, same-key repair restored
the original pattern and saved data with SELinux enforcing. A subsequent signed
Android Updater local install also retained the pattern/setup/test file, with
no further Gatekeeper AVCs. Never remove lock settings or set SELinux permissive
to make this test appear successful.

## Cosmetic sizing on the first release

The very small lock-screen padlock is reproducible at the native 1200×2000,
240 dpi configuration (font scale 1.0; resolution scale 1.0), without a display-size
override. On this non-UDFPS device, SystemUI's `DefaultDeviceEntrySection` creates
a 72 dp device-entry icon container:108 px at density 1.5. The running resource
`com.android.systemui:dimen/lock_icon_padding` resolves to 48 px on **each side**,
and `DeviceEntryForegroundViewModel` passes that padding to the foreground image.
The live view bounds are 108×108 px, leaving only 12×12 px for the drawable.

Device `eb9bc69` adds a SystemUI resource overlay setting
`lock_icon_padding` to 24 dp: at the default density this leaves 36 px (24 dp)
of foreground space inside the unchanged 108×108 px touch target. It also
switches from `full_base_telephony.mk` / `common_full_tablet.mk` to
`full_base.mk` / `common_full_tablet_wifionly.mk`, sets
`PRODUCT_CHARACTERISTICS := tablet`, and removes the unconditional IMS feature
declaration. The cellular product packages (Phone/Dialer, Contacts and Messaging)
are no longer inherited. Shared Qualcomm vendor components and the existing
SKU-specific LTE permission are retained; this does not add SM-P619 support.
No global density or font-scale override is used. See [testing](testing.md)
for build and on-device validation of this follow-up. Runtime lookup now returns
`24.0dip`, and the owner confirms normal icon appearance on the signed update.

The built-in Clock digital home widget is a separate sizing case. A 4×1 widget
on the six-column/five-row launcher grid gets about 684×180 px. DeskClock's
`DigitalAppWidgetProvider` searches for a font that fits **both** dimensions;
one row constrains the clock even when it is wide. The device's maximum widget
clock-font resource resolves to 124 dp, so a low global font cap is not the cause.
Long-pressing the widget and increasing its **height** to two or more grid rows
should allow a larger clock. This is a layout workaround inferred from measured
bounds and source behavior, not a tested resize or a platform rendering fix.
No density/font-scale settings or launcher layout were changed in this audit.
Screenshots and raw diagnostic dumps remain private local artifacts.


## Remaining build/security exceptions

See [the 2026-10-24 audit](build-exceptions-audit.md) for disabled KPTI, three
build-validation exceptions, four vendor ELF-check exclusions, known AVB/vendor
limitations and unresolved runtime policy checks. The audit made no source or
tablet changes; findings are separate from the resolved CFI/VINTF defects.
