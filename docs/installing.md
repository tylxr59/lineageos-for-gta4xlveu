# Installation and updates

## Availability and supported hardware

[The first signed release](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792775790) is available. These instructions describe the tested
Lineage Recovery procedure and its matching release assets. Only
**SM-P613 (2022 Qualcomm Wi-Fi), gta4xlveu** was tested. Do not use these images
for the Exynos 2020 models or LTE variants. The maintainer-tested bootloader/
firmware base was `P613XXS7CXJ1`. The ROM does not flash Samsung bootloader or
modem firmware, so it does not require a downgrade.

The maintainer-tested starting point was an already-unlocked tablet running
danielml3’s LineageOS 23.2 with Lineage Recovery. Unlocking from stock is a
separate process and is not documented as tested here. First installation wipes
userdata.

### Community reports

These were reported by users and not repeated by the maintainer:

- **`P613XXS8CYE1` / bootloader binary 8 from stock One UI** — thanks to
  [Nokuty](https://github.com/Nokuty) ([#2](https://github.com/tylxr59/lineageos-for-gta4xlveu/issues/2)).
  Starting from stock Android 14 (CSC PHE), they unlocked the bootloader, flashed
  the matching `recovery.tar` with Odin 3.14.1 on Windows 11, formatted data and
  sideloaded build 2026-10-29 followed by MindTheGapps (see below). Android 17
  booted and setup completed; the bootloader still reports `P613XXS8CYE1`.
  Wi-Fi, Bluetooth, touch, S Pen, cameras, audio, rotation, USB debugging/charging
  passed basic everyday checks with SELinux enforcing. No long-term battery or
  stability testing was reported. Unlocking trips Knox (warranty bit 1).

## First install from an unlocked device

1. Back up files, authenticate access to needed accounts, and download all assets
   before starting. Keep a copy of the previous ROM/recovery for rollback.
2. Download the release ROM ZIP and its **matching** recovery/vbmeta assets and
   `SHA256SUMS`. Verify checksums on the computer (`sha256sum --ignore-missing -c SHA256SUMS` on Linux checks the files
   you downloaded, or check the individual file hashes).
3. Enter Samsung Download Mode with USB connected: restart using Power + Volume
   Down, then hold both volume buttons as the screen goes black; confirm with
   Volume Up if prompted. With `recovery.img` and `vbmeta.img` from this release
   in the current directory, run (extract `recovery.tar` first with
   `tar -xf recovery.tar` if you downloaded the tar instead of individual images):

   ```sh
   heimdall flash --RECOVERY recovery.img --VBMETA vbmeta.img --no-reboot
   ```

   Both partition transfers were tested on SM-P613 using
   [amo13/Heimdall commit 8378ba4](https://github.com/amo13/Heimdall/tree/8378ba4081875e220d31815ccb7e907112c16481).
   The original Heimdall build encountered connection failures; a fresh blue
   Downloading screen was required for each session. Do not repartition or
   flash unrelated bootloader/modem firmware. `recovery.tar` contains these same
   two images for Samsung flashing tools. Odin is not maintainer-tested, but
   flashing `recovery.tar` with Odin 3.14.1 on Windows 11 worked in a
   [community report](#community-reports).
4. Boot the installed recovery directly: Power + Volume Down until black, then
   immediately Power + Volume Up with USB connected. Confirm **Lineage Recovery
   24.0**. The old 23.2 recovery is not the tested LOS24 installation path.
5. Choose **Factory reset → Format data/factory reset** and confirm.
6. Choose **Apply update → Apply from ADB**, then run:

   ```sh
   adb sideload lineage-24.0-YYYYMMDD-UNOFFICIAL-gta4xlveu.zip
   ```

7. Wait for recovery to report **Install complete**. ADB may finish its progress
   display at about 47%; rely on recovery’s result. A signature error is a reason
   to stop and check the matching package/recovery and published certificate.
8. Choose **Reboot system now**. Complete Android setup. The first startup can
   take longer than subsequent boots.

## Optional Google apps

Google apps are not included or maintainer-tested. A
[community report](#community-reports) installed **MindTheGapps 17.0.0 ARM64**
(`20261022_132445`) by sideloading it in recovery immediately after the ROM,
before the first Android boot. It fit without a space error; Google sign-in,
Play Store and Google services worked. Play Store shows **Device is not
certified**. Play Integrity, banking apps, Widevine/HD streaming and OTA updates
with GApps installed were not tested.

A change from another maintainer’s signing keys, including the local test-key
prototype, is not an ordinary same-key update. A separately verified migration
or clean installation of the first release-key build is required. No unsupported
claim of preserving data across signing identities is made.

## Updates

For this project’s OTA-enabled, same-key release builds:

1. Back up important data and charge the tablet.
2. Open **Settings → System → Updater**, refresh, and download the update.
3. Choose Install and follow the prompts. Recovery installs the package and
   Android restarts. This tablet is non-A/B; there is no seamless inactive slot.
4. Confirm the new build date and normal operation. Ordinary updates do not
   require Factory reset.

Manual fallback: enter matching recovery, choose Apply from ADB, sideload the
new same-key ZIP, confirm success, and reboot **without formatting data**.
This route preserved the owner’s setup/settings during local tests.

The release-key build and a newer same-key local update through Android Updater
have been tested on the owner's SM-P613 without losing the unlock pattern,
setup or saved test data. Updater's **Install local update** also accepts a
matching signed ZIP copied to Downloads. The public feed advertises the signed release; devices on the same build
correctly show no newer update. A major
LineageOS/Android upgrade may have separate migration instructions; do not
assume that a minor-update procedure applies unchanged.

## If startup fails

Return to recovery and collect a redacted recovery log before changing more
partitions. Do not repeatedly wipe data to diagnose boot problems. Samsung
Download Mode is distinct from recovery; fastboot flashing was not supported
by the interface encountered during this port. If restoring a different ROM,
follow its own recovery, key, and data-migration requirements.
