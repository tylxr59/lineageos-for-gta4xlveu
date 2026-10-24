# VINTF kernel compatibility audit

Read-only investigation on 2026-10-24 of public release
`1792787032`, device `eb9bc69`, kernel `75a416868`, vendor `4388d72`.
No source configuration, installed image, tablet setting or release feed was
changed. Findings below are compatibility checks, not a completed CFI build or
hardware validation.

## What VINTF checks

Android's Vendor Interface (VINTF) describes the contract between the Android
framework and device-specific implementation. Manifests describe provided
interfaces; compatibility matrices describe requirements. Kernel requirements
include supported version ranges and configuration options. See AOSP's
[matching rules](https://source.android.com/docs/core/architecture/vintf/match-rules)
and [OTA kernel enforcement documentation](https://source.android.com/docs/core/architecture/vintf/dm#mandating-kernel-requirements-during-ota).

This is distinct from OTA signatures, encrypted user data, SELinux and AVB
verified boot. Passing one does not establish the others. VINTF is also not a
substitute for VTS/CTS or hardware/endurance testing.

## Exact bypass and origin

The released device tree sets
`PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS := false` in `device.mk`.
Inherited commit
[`cf0c60b391aa690b1b9210bff70599c8d3ad1722`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/cf0c60b391aa690b1b9210bff70599c8d3ad1722)
added it with the explanation “Until we fix kernel.” This audit establishes
current failures; the short commit message does not establish all historical
reasons for disabling it.

This does **not** disable all VINTF checks. Released target-files metadata has
`vintf_enforce=true`. The build and OTA tools still check framework/vendor
interfaces, but omit kernel input. The signed target-files archive has neither
`META/kernel_version.txt` nor `META/kernel_configs.txt`; releasetools therefore
skips kernel requirements. Source paths explaining this behavior are
`build/make/core/Makefile` and
`build/make/tools/releasetools/check_target_files_vintf.py`.

The shipped vendor target FCM level is 7. The shipped level-7 matrix explicitly
contains a 4.14 kernel entry with minimum version 4.14.336; the released kernel
is `4.14.357-openela-perf-g75a416868f99`. This failure is not simply that Android17
rejects every 4.14 kernel. These are the actual LineageOS release matrices,
including its legacy-device support, not a claim of stock AOSP certification.

## Checks performed

Used the immutable release's signed target-files archive, extracted VINTF
metadata and all 38 packaged APEXes, and activated those APEXes on the host with
`apexd_host`. Used the existing release-pinned host `checkvintf` tool. Kernel
version, compiler banner and embedded configuration were extracted directly
from that archive's `BOOT/kernel` with `build/make/tools/extract_kernel.py`.

Read-only ADB confirmed the installed build timestamp and kernel release,
normal shell UID2000 and enforcing SELinux. The decompressed live
`/proc/config.gz` exactly equals the configuration extracted from the release
kernel (SHA256
`2ef2974ab28f7d837444dbaac9c03e75502d8cb0cd6485e14da7d28e4c2004c2`).
No root was needed.

Ran `checkvintf --check-compat` with mappings for system, vendor, odm, product,
system_ext and the extracted APEX directory; shipping API30, empty vendor SKU,
and both actual SM-P613 and declared ODM SM-P619 SKU cases. Results agree for
both cases; this does not establish hardware support for SM-P619.

| Host input | Result |
| --- | --- |
| Released metadata, no kernel argument (current bypass behavior) | COMPATIBLE, exit0 |
| Released metadata plus real extracted kernel version/config | INCOMPATIBLE, exit65; missing `CONFIG_AS_IS_LLVM`, `CONFIG_CC_IS_CLANG`, `CONFIG_LD_IS_LLD` |
| Host-only diagnostic config supplying those three markers | INCOMPATIBLE, exit65; ARM64 conditional requirement `CONFIG_CFI_CLANG` fails |
| Host-only diagnostic config also claiming CFI enabled | COMPATIBLE, exit0 |

The last two rows are **counterfactual diagnostics**, not valid replacement
kernel metadata or evidence that the kernel implements CFI. They expose checks
hidden behind the initial failure. Never ship those edited text files or append
claims to OTA metadata to make validation pass. No release archive was edited.

## What is actually missing

The released kernel source has no Kconfig definitions for the three toolchain
markers. The compiler banner embedded in the released image identifies Clang
22.0.2 and LLD22.0.2. Existing assembly build commands invoke Clang without
`-no-integrated-as`. This supports a toolchain-reporting gap: backport correct
Kconfig detection rather than hardcode toolchain claims.

CFI is a substantive difference. The real embedded/live config explicitly has
`# CONFIG_CFI_CLANG is not set`. The shipped matrix's ARM64 conditional group
requires it. This kernel already contains a Clang CFI implementation and has
Clang LTO/ThinLTO enabled, but that does not enable CFI automatically. Its
`arch/Kconfig`, `Makefile` and `kernel/cfi.c` contain the implementation and
integration points. The selected configurations are
`vendor/atoll-perf_defconfig` and `vendor/gta4xlve.config`.

[Control Flow Integrity](https://source.android.com/docs/security/test/cfi)
checks indirect call targets and makes certain memory-corruption attacks harder.
The missing kernel mitigation does not establish a specific exploitable bug,
and does not mean system/userspace CFI is disabled. Other enabled kernel
protections include strong stack protection, shadow call stack, address
randomization, hardened usercopy and seccomp; these do not replace CFI.

## Recommended implementation and validation

1. Start a separate candidate from released kernel/device pins. Preserve the
   paused TI audio branches and keep unrelated experiments out.
2. Backport genuine compiler/linker/assembler identification with correct
   detection for this 4.14 Kbuild. Validate generated config against actual
   tools; adding unknown symbols to a defconfig is insufficient.
3. Enable real kernel CFI and fix demonstrated compiler/linker problems and
   driver type mismatches. Existing CFI code is not proof it builds with the
   current Clang22 toolchain. Temporary diagnostic permissive CFI, if needed,
   must not become the final substitute for enforcement.
4. Re-enable `PRODUCT_OTA_ENFORCE_VINTF_KERNEL_REQUIREMENTS`. Build kernel,
   recovery and ROM; confirm generated target files contain authentic extracted
   kernel version/config and that full VINTF checks run with the kernel input.
5. Validate signatures, source/config continuity and recovery boot, then Android
   boot, credential/data persistence and the hardware matrix. Exercise drivers,
   suspend/wake and repeated boots for CFI violations before a release.

Removing the bypass alone currently fails validation. Weakening the matrix,
spoofing configuration output or suppressing CFI failures would conceal the gap.
A clean host check would establish the declared kernel requirements only;
full compatibility and reliable hardware operation still need their own tests.
The inherited vbmeta/AVB limitation is separate and was not resolved by this audit.
