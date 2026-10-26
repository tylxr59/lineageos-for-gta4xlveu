# Changes

Changes maintained by this project, with links to their implementation commits.
Device, kernel, vendor and shared Pixel HAL links point to separate source
repositories; project links point to documentation, manifests and release tools.
This is not a list of every upstream Android/LineageOS commit: each release's
resolved source manifest records its complete inputs.

Released entries below passed signed installation and hardware smoke checks
recorded in [testing](docs/testing.md). Those checks are not exhaustive hardware
certification. Published releases are immutable; fixes appear in new builds.

## Unreleased

No additional ROM changes staged. Newer diagnostic-only source commits do not
change this release's pinned ROM inputs.

Documentation: [BPF/vendor compatibility audit](docs/bpf-vendor-compatibility.md)
records a live OOM tracepoint-layout mismatch, API/minor-version update gates,
and legacy crypto/protobuf/shim provenance and consumers. No image, library or
device configuration was changed during the audit.

## 2026-10-26 — Security and compatibility

[Release 1793018822](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261026-gta4xlveu-1793018822) · Android 17 / LineageOS 24.0

The exact tested signed build is published with the existing signing identity.
All 12 assets, public ROM/checksum downloads and the eight-entry HTTPS feed were
verified. The tablet already ran this build; no additional older-to-newer public
Updater installation is claimed. Exact source pins remain authoritative even
where linked diagnostic tests have newer commits.

| Change | Implementation commits |
| --- | --- |
| Retain the owning video capabilities for NDK performance points; actual-wrapper sanitizer lifetime tests pass. Signed no-wipe candidate 1792969106, normal codec cleanup and recovery round trip passed; included in this release. | [framework `b911f1a`](https://github.com/tylxr59/android_frameworks_av/commit/b911f1a) |
| Skip optional FUSE-BPF objects only when the kernel program-type entry is absent; retain real read/parse errors and add regression tests. Candidate 1792969106 passed both test ABIs, no-wipe install, storage smoke and recovery checks; included in this release. | [BPF `ee7db63`](https://github.com/tylxr59/android_system_bpf/commit/ee7db63), [lint follow-up `c2621ec`](https://github.com/tylxr59/android_system_bpf/commit/c2621ec) |
| Backport BPF atomic verifier/interpreter support and ARM64 emission, including fetch bounds/subregister fixes and cmpxchg pointer-leak protection. Signed candidate 1793017415 passed live accounting/atomic/DMA-BUF tests, owner hardware checks and recovery round trip; included in this release. | [generic start `d420e8e44`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/d420e8e44), [fetch `56613e4ec`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/56613e4ec), [exchange `8a905eec2`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/8a905eec2), [bitwise `cf273dacb`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/cf273dacb), [bounds `4317c7a6f`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/4317c7a6f), [subregister `a381f62f1`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/a381f62f1), [pointer safety `32fab35c7`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/32fab35c7), [encoders `48c6ea61a`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/48c6ea61a), [ARM64 `30d31b8e1`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/30d31b8e1), [legacy adaptation `e803971c5`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/e803971c5) |
| Test actual LL/SC emitter semantics across 21,840 host cases and prepare bounded live atomic execution/rejection checks. All 43 cases and 1,024 concurrent increments pass on the tablet. | [host `f801061dc`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/f801061dc), [live probe `321c39c9f`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/321c39c9f), [concurrency `72c492f46`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/72c492f46), [probe encoding `a99cbdcd5`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/a99cbdcd5) |
| Adapt legacy FORTIFY for Clang object-size propagation with a real compiler capability gate. Signed candidate 1793018822 passed full build, emitted-call/host bounds checks, no-wipe install, owner hardware and recovery/data checks. | [kernel `931040132`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/931040132), [tests `936030e83`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/936030e83) |
| Enable full refcounts, protected filesystem operations, JIT constant blinding and disabled JIT symbol exports. Candidate 1793018822 passed live cross-owner protection tests and atomic/accounting/DMA regressions with blinding enabled; JIT exports remain disabled despite Android’s privileged-symbol request. | [kernel `739fbedf7`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/739fbedf7), [filesystem tests `6e922a229`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/6e922a229), [fixture setup `26e131e96`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/26e131e96), [capability checks `400e815c0`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/400e815c0) |

## 2026-10-25 — Bluetooth media audio

[Release 1792961358](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261025-gta4xlveu-1792961358) · Android 17 / LineageOS 24.0

| Change | Implementation commit |
| --- | --- |
| Include the AOSP AIDL Bluetooth audio provider and its VINTF fragment so the stack can discover a media audio service. Signed local candidate 1792961358 plays AAC through AirPods Pro2, reconnects and falls back to speakers with separate volumes. Matching recovery/full partition hashes and final Android/data/security/cleanup passed. Rooted debugging remained off. All 12 public assets and the seven-entry HTTPS feed were verified, including a fresh ROM download. | [device `038bb20`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/038bb20) |

## 2026-10-25 — DMA-BUF accounting and thermal queries

[Release 1792944959](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261025-gta4xlveu-1792944959) · Android 17 / LineageOS 24.0

| Change | Implementation commits |
| --- | --- |
| Return successful empty thermal API results for absent sensor/cooling types; preserve real read failures. Repair the native test entry point and add regression tests. | [pixel `d4f83b6`](https://github.com/tylxr59/android_hardware_google_pixel/commit/d4f83b6) |

The thermal service and full ROM compile, signing/host checks pass, and all 11
standalone native tests passed on the tablet. Signed candidate **1792933707**
passed a no-wipe installation, live thermal queries, owner pattern/setup/hardware
checks, matching recovery/full partition hashes, and the final recovery-to-Android
return with encrypted data intact. Its thermal fix is included in release
**1792944959**, together with the DMA-BUF repairs below. See [runtime fixes](docs/runtime-fixes.md).
The opt-in DMA-BUF/BTF kernel experiment is saved on
`wip/los24-dmabuf-iterator`: [host BTF resolver/build repair `bbac598e2`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/bbac598e2),
[conditional fault-injection BTF IDs `2756333ec`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/2756333ec),
and [DMA-BUF iterator `423e21526`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/423e21526).
Both the initial isolated kernel image and the build using committed host-tool
rules compiled successfully. The initial experiment was excluded from the thermal-only candidate.
The completed repairs below are enabled in this release. A subsequent [DMA-BUF candidate](docs/dmabuf-accounting.md) fixes legacy
multi-read resumption ([52847c63d](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/52847c63d)),
enables the device test config ([0618060fb](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/0618060fb)),
adds lifecycle tests ([40dd1806a](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/40dd1806a))
and adapts the host build to Android's LLVM tools ([1d5531f9a](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/1d5531f9a)).
Full ROM/host checks passed, but candidate 1792935924 **bootlooped and is rejected**.
Working thermal ROM1792933707 was restored without wiping. The follow-up repairs
the BTF parser's obsolete linker symbols
([4823beeb2](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/4823beeb2))
and inherited type/string limits plus error propagation
([8861e8c76](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/8861e8c76)).
The parser-repair bundle passed host checks but was superseded before flashing.
The next candidate also backports upstream's perf type-name disambiguation
([4c536a5bc](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/4c536a5bc))
and requires iterator/helper type IDs to agree. Corrected candidate 1792942729 passed build/signature/VINTF/host checks and a
no-wipe boot with data/hardware intact. BTF setup worked, but DMA accounting
was then blocked by missing ARM64 JIT probe-load support. The corrected candidate adds
upstream exception handling ([282b0b486](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/282b0b486)),
the later user-address guard ([ecf66a6f9](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/ecf66a6f9))
and source-based host tests ([dc07aa16f](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/dc07aa16f)).
Signed candidate **1792944959** now boots with working pinned DMA-BUF accounting.
The live test found all 1,024 owned buffers exactly once at four read sizes,
passed concurrent allocation/free and 200 early-close checks with no owned
buffers retained. The owner confirmed setup and hardware smoke checks. Matching
recovery/full partition hashes and final Android return, encrypted-data
persistence and security/cleanup checks passed; Rooted debugging is off.
The owner subsequently authorized publication. All 12 public assets and the
six-entry HTTPS feed were verified, including a fresh ROM download.
TI speaker processing remains an
experiment, with no released audio tuning change.

## 2026-10-24 — Thermal reporting and launch hints

[Release 1792894491](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792894491)

| Change | Implementation commits |
| --- | --- |
| Configure reporting-only CPU/GPU/battery thermal sensors; give the service an exact executable label and narrow Power HAL/property access. | [device `06447b4`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/06447b4), [device `72a336a`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/72a336a), [device `8289416`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/8289416) |
| Declare the thermal statistics dependency and start the thermal HAL before the framework waits for it. The earlier boot-completed trigger caused a startup dependency cycle and was rejected. | [device `d61cc85`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/d61cc85), [device `f38d06f`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/f38d06f) |
| Correct the LLCC bandwidth request from unsupported value 8137 to 8136, with a configuration guard. | [device `c48d6cf`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/c48d6cf) |
| Remove obsolete ART compiler-filter and unused SurfaceFlinger settings. | [device `e1fe429`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/e1fe429) |
| Publish tested source pins, OTA metadata and validation records. | [project `f2f258c`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/f2f258c), [project `5ff463e`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/5ff463e), [project `6597c16`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/6597c16) |

Thermal reporting adds no cooling controller or fabricated skin sensor. Launch
trace samples did not establish a general speed gain; no battery gain is claimed.

## 2026-10-24 — USB File Transfer and hardening

[Release 1792876959](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792876959)

| Change | Implementation commits |
| --- | --- |
| Give the QTI USB gadget HAL sole ownership during normal Android boot; retain the legacy charger-mode path. Fixes File Transfer reverting and duplicate ADB interfaces. | [device `02b4ef7`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/02b4ef7) |
| Stop forcing KPTI off; enable it in the kernel and preserve NZCV/task mode across the SSBD return path. Include the upstream Kryo Silver CPU identification fix. | [device `fe6bc40`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/fe6bc40), [kernel `71bb88b5f`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/71bb88b5f), [kernel `18eeda8c4`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/18eeda8c4), [kernel `cae626ff7`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/cae626ff7) |
| Restrict unprivileged kernel-log access. | [kernel `0c5ccf4fc`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/0c5ccf4fc) |
| Restore proprietary-library dependency declarations and enforce ELF/duplicate-module checks; reject ELF prebuilts copied outside modules. | [device `8939dfa`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/8939dfa), [device `e6d8d24`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/e6d8d24), [vendor `1c0a6f2`](https://github.com/tylxr59/android_vendor_samsung_gta4xlveu/commit/1c0a6f2) |
| Label hardware-statistics sysfs nodes and exclude unused vendor factory-test policy while retaining common QTI types. | [device `b1995e3`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/b1995e3), [device `5f6344e`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/5f6344e), [device `4a8b4e6`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/4a8b4e6) |
| Reuse inherited wakeup labels and retain the platform virtual-wakeup label to avoid duplicate policy definitions in Android/recovery. | [device `05c3082`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/05c3082), [device `b07f055`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/b07f055) |
| Record USB transfer/reconnect, recovery and encrypted-data tests; publish the validated OTA. | [project `e24a424`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/e24a424), [project `785febb`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/785febb), [project `c610a91`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/c610a91), [project `7290e12`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/7290e12) |

AVB verification-enabling was rejected by the Samsung bootloader and rolled
back. It is **not** a shipped hardening feature; the bootloader remains unlocked.

## 2026-10-24 — VINTF, enforcing CFI and upstream maintenance

[Release 1792851872](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792851872)

| Change | Implementation commits |
| --- | --- |
| Repair LLVM symbol reporting so CFI builds correctly, and enforce CFI instead of permissive mode. | [kernel `793125bc3`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/793125bc3) |
| Enforce VINTF kernel requirements during OTA construction. | [device `12c0e2d`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/12c0e2d) |
| Integrate 18 reviewed LineageOS common-kernel cgroup/freezer maintenance commits. | [kernel `88b63b7ae`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/88b63b7ae) |
| Record the combined upstream LineageOS update, hardware/recovery validation and published source pins. | [project `58b7a4e`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/58b7a4e), [project `7b211ce`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/7b211ce), [project `ffceedd`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/ffceedd) |

## 2026-10-23 — Wi-Fi tablet configuration and lock-screen UI

[Release 1792787032](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792787032)

| Change | Implementation commits |
| --- | --- |
| Use the Wi-Fi tablet product; remove bundled Phone, Contacts, Messaging and STK plus the incorrect IMS feature. Set the lock-icon padding to 24dp at native 240dpi. | [device `eb9bc69`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/eb9bc69) |
| Pin the tablet fixes and record real public Updater/recovery/data-preservation checks. | [project `4fca86c`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/4fca86c), [project `6e122d8`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/6e122d8), [project `016e3d3`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/016e3d3) |

## 2026-10-23 — First public signed release

[Release 1792775790](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792775790)

| Change | Implementation commits |
| --- | --- |
| Adapt recovery init and vendor ueventd configuration for Android 17. | [device `e44d4d7`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/e44d4d7), [device `78014df`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/78014df) |
| Retain the Samsung reserved display-dump device-tree node needed for boot. | [kernel `75a416868`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/75a416868) |
| Use the QTI AIDL USB controller. | [device `44bda91`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/44bda91) |
| Configure the maintained v2 Updater feed. | [device `d4723ed`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/d4723ed) |
| Include narrow TEE Gatekeeper storage rules in active vendor policy, preserving saved lock patterns across updates. | [device `4c68bc9`](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/4c68bc9) |
| Create installation/build/agent guidance, pinned manifests and OTA tooling. | [project `2fa5bc2`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/2fa5bc2), [project `26587e2`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/26587e2) |
| Add persistent private release signing, backup and verification workflows; deduplicate mapped OTA trust certificates and reject duplicate trust ZIP entries. | [project `92c201c`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/92c201c), [project `b123e93`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/b123e93) |
| Document signed updates and recovery flashing; publish and verify the first real HTTPS Updater installation with encrypted data intact. | [project `964271a`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/964271a), [project `f79dc2d`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/f79dc2d), [project `c08e6b5`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/c08e6b5), [project `b1eb4bb`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/b1eb4bb) |

## Maintenance and investigations

These records help future maintainers; they do not imply additional shipped
features.

| Change | Implementation commits |
| --- | --- |
| Audit remaining compatibility/security gaps against release1792961358; reproduce codec-catalog teardown failure and wakelock BPF instruction mismatch; consolidate the current test overview. No ROM change. | [project `8a69758`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/8a69758) |
| Add a reusable fail-closed BTF boundary/limit/iterator-helper identity preflight, including optimized-Python rejection checks. | [project `4444cd7`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/4444cd7) |
| Add commit-linked release history and require future maintenance entries. | [project `b65fab2`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/b65fab2) |
| Document exact upstream branches and the routine update workflow. | [project `e3037f0`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/e3037f0), [project `02aae54`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/02aae54) |
| Audit TI speaker feedback and Dolby paths. The TI prototype sounded clearer, but production routing/lifecycle validation remains unfinished; Dolby mainly increased volume. Normal audio was restored. | [project `ff9eb2b`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/ff9eb2b), [project `71be255`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/71be255), [project `758bf6b`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/758bf6b) |
| Record the battery test protocol and runtime-log audit. | [project `7b2c0c9`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/7b2c0c9), [project `a0116a0`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/a0116a0) |
| Record the thermal API regression tests and isolated DMA-BUF investigation. | [project `f8917fd`](https://github.com/tylxr59/lineageos-for-gta4xlveu/commit/f8917fd) |

When changing maintained code or release tooling, add the implementation commit
here. Keep uninstalled candidates under **Unreleased**; move them into a release
entry only after the runbook's installation and publication checks. Link source
commits, distinguish documentation from implementation, and keep private logs,
credentials and device identifiers out of this file.
