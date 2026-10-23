# Installation and updates

## Availability and supported hardware

No public release is available yet. These instructions describe the tested
Lineage Recovery procedure and the required future release assets. Only
**SM-P613 (2022 Qualcomm Wi-Fi), gta4xlveu** was tested. Do not use these images
for the Exynos 2020 models or LTE variants. The tested bootloader/firmware base
was `P613XXS7CXJ1`; other firmware bases have not been validated.

The tested starting point was an already-unlocked tablet running danielml3’s
LineageOS 23.2 with Lineage Recovery. Unlocking from stock is a separate process
and is not documented as tested here. First installation wipes userdata.

## First install from an unlocked device

1. Back up files, authenticate access to needed accounts, and download all assets
   before starting. Keep a copy of the previous ROM/recovery for rollback.
2. Download the release ROM ZIP and its **matching** recovery/vbmeta assets and
   `SHA256SUMS`. Verify checksums on the computer (`sha256sum -c SHA256SUMS` for
   all listed downloaded files, or check the individual file hashes).
3. Enter Samsung Download Mode with USB connected: restart using Power + Volume
   Down, then hold both volume buttons as the screen goes black; confirm with
   Volume Up if prompted. Use the release’s recovery/vbmeta tar with a compatible
   Samsung flashing tool, or its documented Heimdall image commands. Do not
   repartition or flash unrelated bootloader/modem firmware.
4. Boot the installed recovery directly: Power + Volume Down until black, then
   immediately Power + Volume Up with USB connected. Confirm **Lineage Recovery
   24.0**. A ROM release must supply tested commands/assets for this step before
   public use; the old 23.2 recovery is not the tested LOS24 installation path.
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
matching signed ZIP copied to Downloads. The public feed is currently empty;
public download/install remains pending the first authorized release. A major
LineageOS/Android upgrade may have separate migration instructions; do not
assume that a minor-update procedure applies unchanged.

## If startup fails

Return to recovery and collect a redacted recovery log before changing more
partitions. Do not repeatedly wipe data to diagnose boot problems. Samsung
Download Mode is distinct from recovery; fastboot flashing was not supported
by the interface encountered during this port. If restoring a different ROM,
follow its own recovery, key, and data-migration requirements.
