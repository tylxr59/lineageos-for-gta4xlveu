# Build and security exceptions audit (2026-10-24)

Historical baseline: read-only review of released build **1792851872**, device `12c0e2d`, kernel
`88b63b7ae`, vendor `4388d72`. No ROM source, tablet setting, root mode or public
feed was changed. This is a targeted configuration audit, not a complete
security assessment, CTS/VTS run or vulnerability scan.

The follow-up below records fixes and device tests after this baseline audit.
The owner later authorized release 1792876959, which includes these tested fixes
and the device-only USB correction; public manifests/feed now identify that build.

## Kernel page-table isolation: original finding

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


## Hardening follow-up (in progress)

The KPTI-only build compiled and passed strict VINTF/signature validation but
failed to boot. A temporary fault diagnostic identified init's invalid frame
pointer and SIGSEGV on return to userspace. Review of the actual kernel binary
found that `apply_ssbd` changed NZCV after the native/compat task-mode test;
KPTI's later conditional branch could select the wrong trampoline and corrupt
userspace x29. Kernel commit `18eeda8c4` repeats the saved task-mode test after
`apply_ssbd`, retaining both mitigations. The diagnostic logging is excluded.

That corrected boot image has now booted on the owner's tablet. Live config
confirms KPTI and enforcing CFI; Meltdown sysfs reports **Mitigation: PTI**.
Android completed boot, encrypted data unlocked, the saved-file checksum
persisted, SELinux remained enforcing, ordinary ADB was UID2000 and Rooted
debugging was off. The owner confirmed the original pattern/setup, Wi-Fi, both
cameras, speakers and S Pen. This is a boot-component test with the KPTI candidate
userland, not yet a complete hardening ROM/recovery validation or public release.

The combined candidate also backports upstream Linux
[`f4617be35b4b`](https://github.com/torvalds/linux/commit/f4617be35b4b547e82d30993f56d631dfc2d5f88),
which identifies Kryo 3xx/4xx silver CPUs as Meltdown-safe, with the required
upstream MIDR definitions. The tablet's silver part is 0x805. This does not
blanket-mark the gold CPUs safe, change existing vendor erratum matching, or
turn off KPTI's KASLR protection. The combined candidate reports **Not affected**
in Android; matching recovery explicitly detects KPTI and forces it on for
KASLR. These remain kernel reports, not independent CPU certification.

### Combined build and device checks passed

All three `BUILD_BROKEN_*` switches have been removed in the candidate device
branch. Restored ELF checks pass for all six ABI/module variants of the four
previously exempt modules. Missing media dependencies now build from existing
source; the LOWI executable declares its existing libwpa_client dependency.
Extraction regeneration also creates the six Adreno symlinks already specified
by the proprietary list. No proprietary binary was modified. The full image build passed with copy
checks and partition filtering active.
The final target files include both ABI variants of libc2dcolorconvert and
libplatformconfig, and the six audited proprietary ELF variants match the
published baseline byte for byte.

The policy candidate labels actual SM5714 battery paths and wakeup statistics,
uses the existing vendor sensor label, and gives tee a dedicated QSEECom status
property type. It excludes four unused Qualcomm vendor test-policy directories.
Complete policy/neverallow compilation and image policy checks passed. Live
matching-recovery checks confirm all 51 wakeup targets and three SM5714 battery
attributes have the intended labels; vendor sensor child labels are present.
Ordinary Android ADB cannot expose the full kernel audit stream, so this does
not establish elimination of every legacy denial. Common HAL references required retaining
the vtloopback app declaration and three existing property types/labels outside
the excluded test directories, without restoring factory-test grants. Duplicate
genfs labels already supplied by Qualcomm/platform policy were removed. No
broad generic-sysfs/default-property allow, permissive workaround or new
denial-suppression rule was added.

The baseline compiled policy contains nine permissive domains inherited through
userdebug/Qualcomm policy: su, backuptool, qti-testscripts and six vendor test
domains. None was active in the captured process snapshot. The combined
candidate's compiled policy confirms all six vendor test domains are removed;
only su, backuptool and qti-testscripts remain. Ordinary userdebug's remaining
permissive domains must be disclosed,
not confused with globally permissive SELinux or app-root availability.

### Verified Boot experiment: blocked by Samsung trust

A flags-0 vbmeta using the existing AVB identity passed offline signature,
boot/DTBO hash and all five dynamic-partition hashtree checks. On the tablet,
Samsung's bootloader rejected it with **“public key used to sign data rejected.”**
The exact original vbmeta was restored, and Android booted/unlocked afterward.
No wipe or bootloader relock occurred. No supported custom-key enrollment has
been established. Flags-3 vbmeta therefore remains a demonstrated platform
limitation; OTA authentication does not imply enforced boot-time integrity.

### Other reviewed boundaries

- No newer maintained proprietary vendor drop was found. The inherited list
  identifies P619XXSACYD1 shared-maintainer blobs; the vendor patch date remains
  May 2025. Platform updates cannot supply missing closed-firmware fixes.
- BPF default-off is not blindly enabled: this legacy syscall's privilege check
  precedes command dispatch and would also reject pinned-map operations used
  by Android services without CAP_BPF/CAP_SYS_ADMIN. For example, system_suspend
  has only BLOCK_SUSPEND capability and opens/reads a pinned BPF statistics map.
  SELinux and existing capability checks
  remain relevant. A compatible restriction requires separate work.
- `perf_event_paranoid=-1` is deliberately set by AOSP's Perfetto init policy;
  SELinux perf hooks are present. ART uses userfaultfd, whose kernel-fault mode
  already has a privilege/default-sysctl gate. Neither feature is disabled just
  because it appears in an attack-surface list.
- The candidate boots Android and recovery with restricted kernel-log access.
- H.264 encoder/decoder creation works on the baseline and corrected KPTI boot.
  The legacy software MPEG4/H263 OMX names are absent from the actual CAF
  registry even though XML advertises them. Restoring ELF checks does not fix
  that independent metadata/codec limitation.

Candidate sources are on `fix/los24-hardening` in the three maintained forks.
At this test stage, release manifests/feed still described1792851872. The later
release 1792876959 includes these fixes. Performance, suspend/battery and full CTS/VTS remain
separate validation gaps.


### Signed candidate 1792860066

The complete combined build passed, including strict target-files VINTF with
actual embedded kernel config matching OTA metadata. All APK/APEX, recovery
trust, component AVB and whole-file OTA signature checks passed with the existing
pinned identity. Kernel config has enforcing CFI, KPTI and restricted dmesg.
Exact sources: device `b07f055`, kernel `0c5ccf4fc`, vendor `1c0a6f2`; all other
1,239 projects match the public release. See the
[candidate source manifest](../manifests/candidates/hardening-20261024.xml).

Signed no-wipe installation, Android boot and matching recovery boot passed.
Full boot/DTBO/recovery partition hashes match the signed package; original
vbmeta is unchanged. The original pattern/setup, saved-file checksum, file
encryption, enforcing SELinux, normal ADB and Rooted debugging off passed,
including the recovery-menu return to Android. The owner confirmed Wi-Fi,
both cameras, speakers, S Pen and auto-rotate. Temporary probe/test files were
removed. This intermediate test build was not published; its fixes are included
in the later public release 1792876959. See [testing](testing.md) for the candidate digest and limitations.


### Boot-only diagnostic hazard: automatic recovery updating

The temporary corrected boot image was tested with the earlier KPTI userland.
That userland's install-recovery script full-flashes its bundled older recovery
when the partition hash differs. The subsequent sideload reboot bootlooped;
restoring the known-good recovery allowed the pending sideload to start. This
is consistent with automatic recovery updating having restored the earlier
broken recovery; its partition was not read back before restoration, so this
specific transition is an inference. No ROM transfer or wipe preceded it.

The final package's vendor recovery payload and updater SHA1 target were checked
against its signed recovery image; they match. After installation, the actual
recovery partition hash and recovery boot also matched. For future boot-only
diagnostics, account for automatic recovery updating and verify the recovery
partition after Android boots. A boot-only flash does not preserve recovery
indefinitely when the installed updater contains another image. Prefer a complete
matched candidate, or deliberately manage and restore the Updater recovery-update
setting within the authorized test scope. If a restored recovery shows “No
command,” check `adb get-state`: a pending `sideload-auto-reboot` request can
already have placed it in sideload mode.
