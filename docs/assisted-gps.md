# Assisted GPS and Qualcomm XTRA

## Finding in release 1793039898

The vendor `xtra-daemon` requests `path1.xtracloud.net`, `path2.xtracloud.net`
and `path3.xtracloud.net` to obtain satellite assistance data. On the inspected
tablet, DNS blocking returned `0.0.0.0`; all three connections failed and the
daemon scheduled a 300-second retry. These requests continued after disabling
Assisted GPS. The framework logged the setting callback before another request
cycle from the same running process. This attributes those queries; it is not a
complete malware audit or evidence about successful HTTPS request metadata.

Settings writes `assisted_gps_enabled`, and `GnssLocationProvider` writes
`persist.sys.xtra-daemon.enabled`. Lineage's source GPS utility has a consumer
for this property in process configuration parsing. This product instead uses
Samsung's preferred prebuilt `libgps.utils`, which lacks that control. Both ABI
libraries in the exact signed release archive match the vendor prebuilts. The
prebuilt launcher imports `loc_read_process_conf` from that library. A shell
`getprop` returning blank is not evidence the property is unset: ordinary shell
is denied access to `xtra_control_prop` by SELinux.

## Released implementation

The paired device and vendor commits move XTRA supervision to Android init:

- Disable only the `xtra-daemon` entry in vendor `izat.conf`, preventing the
  launcher from starting or respawning a duplicate.
- Define a disabled init service for the existing `/vendor/bin/xtra-daemon`,
  keeping UID/GID `gps`, supplementary groups `inet` and `system`, and its existing
  `vendor_location_exec` to `vendor_location` SELinux transition.
- Start it when the framework control property is true and boot is complete.
  Both property changes trigger evaluation, so a saved enabled setting works
  across boot. Missing or false control cannot start it through class startup.
- Stop it when the property becomes false. Init's explicit stop disables crash
  restart until a subsequent start, providing live off/on behavior.

No native executable, shared library, GNSS HAL, location policy permission,
other launcher entry or signing identity is changed. Framework control,
including its existing emergency handling, is retained. The fix controls XTRA;
it does not claim to disable every vendor network or location function.

Implementation: [device commit](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/1099a44a51f34475b2c32011e1854828fb658610),
[vendor commit](https://github.com/tylxr59/android_vendor_samsung_gta4xlveu/commit/ec725c3b9a88845f9ebe7b37a01fa1b23619d595).
Candidate [resolved manifest](../manifests/candidates/assisted-gps-20261029.xml)
and [fork pins](../manifests/candidates/assisted-gps-forks-20261029.xml) change
only device and vendor among the 1,242 released project revisions. Released
manifests and OTA feed now identify the tested build 1793279242.

## Release 1793279242 — validation complete

The exact candidate ROM is signed with the existing persistent identity and has
been installed through recovery without wiping. The owner authorized publication after local validation. Public release/feed
and source pins now identify the exact tested build1793279242. ROM SHA256:
`2228d2fd11dff98a99394ddecb0a1418e9b6847ec8bf06305dc37863b4de6135`.

Full target-files/recovery build, strict VINTF, image checks, APK/APEX signatures,
actual recovery OTA trust, AVB signatures and whole-file OTA signature passed.
Component verification covered 120 standalone APKs, 37 APEX containers/payloads
and 26 nested APKs, retaining the presigned CTS shim. Recovery trusts the one
existing OTA certificate. No keys were regenerated or signing identity changed.
The generated recovery installer refers to the exact bundled signed recovery.
Standalone development vendorimage output is not the installation bundle.

All 1,655 compared vendor bin/lib archive entries, including symlinks, match the
released signed target files, excluding the generated recovery installer. The
kernel/config, boot and DTBO images, compiled policy, audio, USB and thermal
components match the release. The paired XTRA init/izat configuration is present
in the actual candidate. Standalone and full-product init verification pass.

### Device evidence

- Signed no-wipe sideload returned success and Android booted candidate1793279242.
  The owner confirmed the usual pattern, normal home screen/setup and all
  available hardware smoke checks. Encrypted FBE, enforcing SELinux, saved setup
  flags and a checksum-verified temporary data marker persisted across testing.
- Two live off/on cycles passed. Enabled XTRA is exactly one init child with
  primary UID/GID `gps`, supplementary `inet`/`system`, `vendor_location` context
  and zero permitted/effective/ambient capabilities. Init omits the launcher's
  redundant supplementary primary GPS group; the effective group set is equal.
  Other launcher/GNSS HAL/LOWI process IDs remained stable through toggle tests.
- A real enabled positive control captured six outgoing A/AAAA questions for
  path1/path2/path3.xtracloud.net, with no packet drops. Startup download attempts
  can be delayed; a short 30-second capture was insufficient. Two transient
  default-network DNS cache flushes were used while establishing the capture;
  DNS settings and blocking rules were unchanged. Downloads remained blocked.
- Disabling stopped XTRA. A 720.6-second observation with 47 state samples and a
  hostname-filtered IPv4 UDP DNS capture found zero matching questions, zero
  XTRA processes/respawns and zero packet drops. Other location processes stayed
  stable, including while an ordinary foreground GPS request was active.
- A fresh reboot with the setting enabled retained it and started one correctly
  supervised daemon. After switching off, an actual matching-recovery boot and
  owner menu return retained setting0 and no XTRA process. Rooted inspection
  established property/service behavior; ordinary shell cannot read the
  `vendor_default_prop` service-status property, and blank output is not treated
  as proof of a stopped service.
- Actual recovery kernel/config and full boot/DTBO/recovery partition hashes
  matched the signed candidate. Original live vbmeta remained unchanged. No
  manual vbmeta flash, relock, wipe or fresh recovery/vbmeta-pair installation
  was performed or claimed.
- With Assisted GPS off, the temporary ordinary GPS probe recorded 94 fresh,
  nonmock GPS fixes with up to 23 satellites used. The owner also confirmed fixes.
  The probe recorded satellite counts, fix counts, reported accuracy and age;
  it had no network/storage permission and did not record coordinates. This is
  a functional fix test, not a cold-start or accuracy benchmark; cached assistance
  was not cleared.
- Final normal ADB UID2000, Rooted debugging off, encrypted/unlocked FBE,
  enforcing SELinux and empty crash buffer passed. The temporary probe, owned
  data marker, capture processes, PID files and root helper were removed.
  Assisted GPS remains off and the screen-awake setting remains0.

The [published 12-asset bundle](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261029-gta4xlveu-1793279242) is this exact tested ROM, including
matching recovery and correctly padded 64KiB signed vbmeta. All asset sizes and
GitHub SHA256 digests, downloaded checksums, fresh public ROM hash and canonical
10-entry HTTPS feed on host/tablet matched. Released source pins match all 1,242
tested projects. No rebuild, re-sign or new keys were used for publication.
No new public HTTPS Updater installation is claimed for this candidate. These
bounded checks do not constitute battery/performance or CTS/VTS certification.
