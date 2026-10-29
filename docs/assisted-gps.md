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

## Unreleased fix

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
manifests and OTA feed continue to identify 1793039898.

## Validation

The configured Android build completed `vendorimage`, `selinux_policy`,
`host_init_verifier` and `check-vintf-all` successfully. Standalone and full-product
init verification pass against the built property contexts and account files.
The generated vendor filesystem contains the exact new init file and paired
izat.conf. All 1,454 compared vendor binary/library files match the signed release
byte for byte, and the compiled policy is identical (SHA256
`b30484e2b3b574fd6b31d9e82221688da15db0c57a8ecdb1487cc065de374a2d`).
Only the XTRA process state changes in the effective izat.conf content.

This vendor image is a development validation artifact, not a complete signed
installation bundle. Target-files packaging creates the recovery installer and
recovery payload; the generated installer script is absent from this standalone
vendorimage staging tree and is excluded from the 1,454-file comparison. A future
install requires complete target-files packaging, persistent-key signing and
normal image/signature validation. Source and build checks do not establish
live DNS suppression or GPS functionality.

Before installing a candidate, verify the packaged init file and the disabled
XTRA stanza together; deploying either half alone is incomplete. Verify all
vendor executables and libraries remain byte-identical to the release, and all
other izat.conf process stanzas are unchanged.

Device acceptance checks on a signed, no-wipe candidate:

1. Boot with Assisted GPS off. Check `init.svc.vendor.xtra-daemon` is stopped and
   no XTRA process or fresh XTRA queries appear over at least two retry periods.
   Confirm the launcher, GNSS HAL and other expected location children remain.
2. Enable Assisted GPS. Check exactly one XTRA process, parent PID 1, expected
   UID/groups/SELinux context, and service running. Existing DNS blocking may
   remain: download success is a separate test and must not be inferred.
3. Disable while running. Check immediate service/process stop and no retries
   for at least 10–15 minutes. Verify no launcher respawn or crash restart.
4. Repeat off/on and reboot with each saved setting. Confirm intended state
   without manually killing services or altering SELinux.
5. Test ordinary GNSS location outdoors in standalone mode and assisted mode,
   then normal location toggles and hardware/data/security smoke checks.
   Record whether assistance downloads actually succeeded under the DNS policy.

Runtime, reboot, DNS-suppression, GNSS and signed installation checks are pending.
No new ROM installation or publication is claimed by this implementation record.
