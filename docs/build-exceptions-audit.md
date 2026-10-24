# Build and security exceptions audit (2026-10-24)

Read-only review of released build **1792851872**, device `12c0e2d`, kernel
`88b63b7ae`, vendor `4388d72`. No ROM source, tablet setting, root mode or public
feed was changed. This is a targeted configuration audit, not a complete
security assessment, CTS/VTS run or vulnerability scan.

## Kernel page-table isolation: investigate next

`BoardConfig.mk` includes `kpti=off`. The actual embedded/live kernel config has
`# CONFIG_UNMAP_KERNEL_AT_EL0 is not set`, inherited from
`arch/arm64/configs/vendor/atoll-perf_defconfig`. Removing the boot argument alone
would therefore not enable isolation. The live Meltdown vulnerability sysfs
entry reports **Vulnerable**.

This is a real disabled mitigation and a useful next hardening investigation.
It does not by itself prove physical susceptibility or an exploitable path.
The legacy kernel's `unmap_kernel_at_el0()` uses a CPU-ID safe list and feature
registers; Qualcomm MIDRs need device-specific review. Do not infer that a
Qualcomm core is covered by an Arm-branded safe-list entry merely because of
its architectural lineage. No exploit or CPU susceptibility test was performed.
The same code also considers isolation useful for KASLR robustness.

A future candidate should review CPU applicability and driver constraints,
enable the actual kernel feature, remove the forced-off argument and validate
build/Android/recovery/data unlock, performance and suspend. Do not silently
change the published kernel or claim all speculative-execution issues are fixed.
Live Spectre-v1 reports user-pointer sanitization; Spectre-v2 reports Not affected;
speculative-store-bypass reports mitigation via prctl. These are kernel reports,
not independent hardware certification.

## Build validation exceptions

The device BoardConfig enables three inherited compatibility switches:

| Switch | What it relaxes | Consequence |
| --- | --- | --- |
| `BUILD_BROKEN_DUP_RULES` | Duplicate build-rule rejection | Can hide conflicting output producers. |
| `BUILD_BROKEN_ELF_PREBUILT_PRODUCT_COPY_FILES` | Rejection of executable/shared-library copies through `PRODUCT_COPY_FILES` | Bypasses the normal prebuilt-module installation path for those copies. |
| `BUILD_BROKEN_INCORRECT_PARTITION_IMAGES` | Partition file-list filtering | Previously staged files can enter an image even when absent from current product module selection. |

The current checked-out build code still consumes these switches. In particular,
`build/make/core/Makefile` omits image input-directory filters when the last one
is set. See [AOSP build-system changes](https://android.googlesource.com/platform/build/+/refs/heads/android16-qpr2-release/Changes.md).
These are validation/reproducibility debts, not proof of corrupt or contaminated
release images. No specific unintended release file was demonstrated here.
Remove them separately in future candidates and fix the resulting actual build
errors; do not mass-delete switches and assume compilation is sufficient.

The vendor Android.bp also explicitly sets `check_elf_files: false` on four
modules: `libOmxSwVdec`, `libOmxSwVencMpeg4`, `libapex_cmn` and `lowi-server`.
That skips their build-time ELF consistency checks. It does not disable the
runtime linker, prove missing dependencies or establish a working ABI. Review
each blob's dependencies/exports and exercise the relevant media/location paths
before removing an exception. Legacy libcrypto/UI shims are separate documented
ABI adaptations, not automatic evidence of a security bypass.

## Verified Boot remains a known limitation

The product generates vbmeta with flags **3**, combining disabled verification
and disabled hashtree verification. The live boot state is **orange**. Existing
release keys authenticate the OTA and signed components; that is separate from
boot-time integrity enforcement. The signed vbmeta assets were host-verified,
but this routine update retained the earlier live vbmeta partition.

See [signing](signing.md), [AOSP Verified Boot](https://source.android.com/docs/security/features/verifiedboot/verified-boot)
and [boot states](https://source.android.com/docs/security/features/verifiedboot/boot-flow).
Do not claim stock-like locked verified boot or advise relocking this Samsung
bootloader. A future AVB experiment must preserve a recovery path and review
Samsung bootloader behavior and all chained descriptors; changing flags alone
is not a demonstrated solution.

## Legacy vendor and remaining policy work

The vendor patch level remains **2025-05-01**, while the Android platform reports
**2026-10-01**. Updating LineageOS does not update closed Samsung/Qualcomm firmware
and HALs. The [upstream audit](source-upstream-audit.md) records the maintained
vendor boundary; patch dates do not establish provenance of every individual blob.

Previous startup captures contain sysfs/property SELinux denials. The device is
still enforcing; broad permissive policy was not used to hide them. Determine
which denied operations are necessary before writing narrow rules. `dontaudit`
entries suppress selected denial logging while leaving access denied; they are
not allow rules. This audit found no device-tree permissive-domain declaration
or ignore-neverallow switch, but did not independently enumerate every compiled
platform/vendor policy rule.

The kernel config also has BPF's default-off option unset, userfaultfd enabled,
and the live shell can read `perf_event_paranoid=-1`. Those warrant a separate
attack-surface review. Ordinary ADB cannot read the relevant BPF/userfaultfd and
pointer/dmesg sysctls under current permissions; their effective restrictions
and untrusted-app access were not established. SELinux/permissions matter, so
configuration presence alone is not evidence that apps can use those interfaces.

## Things not to mislabel as defects

- `userdebug` is the normal development variant here. Rooted debugging is off;
  ADB is UID2000, authenticated, and SELinux is enforcing. No app-root was added.
- The command line initially sets `lpm_levels.sleep_disabled=1`, but the vendor
  post-boot script explicitly writes it back to 0. Normal shell could not read
  the live parameter, so the boot argument alone is not evidence that deep sleep
  is disabled all night. Battery/suspend testing remains separate.
- The source's development recovery test key is replaced by persistent private
  keys during release signing; the shipped image was verified separately.
- Kernel CFI is now enforcing and real VINTF kernel checks pass. This audit
  found no second device-level VINTF bypass.

Suggested order: investigate KPTI, remove build-validation exceptions one at a
time, then triage useful SELinux denials and kernel attack-surface restrictions.
Keep AVB/bootloader experiments separate from routine updates.
