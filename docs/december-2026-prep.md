# December 2026 update preparation

Checked and prepared November 25, 2026 against released build **1793916221**
and its 1,242-project resolved manifest. The owner chose to integrate merged
upstream changes now and wait for the December security series before signing,
installing or publishing. Nothing on this page is released or installed; the
public feed and `manifests/resolved.xml` remain build 1793916221.

## Upstream state at the check

| Source | Live head | Relevance |
| --- | --- | --- |
| LineageOS/android `lineage-24.0` | `913c6baa35ffa32be9ae33368cac69dbec6ead4b` | One commit: tracks an sm8850 audio project. AOSP tag still `android-17.0.0_r1`. |
| Shared Qualcomm kernel `lineage-20` | `d0956ce5966c75f078359d1c2d8a870dc8836ee6` | Two of_node leak fixes in qpnp-qg/qpnp-fg-gen4 above integrated base `bae1ba425fe3`. Neither driver is built by `atoll-perf_defconfig` + `gta4xlve.config` (QG explicitly `=n`). Clean merge-tree preview; not integrated. |
| Sevenrock device `lineage-24.0` | `b06860fad224a6c5cbcfa3cd4a0abff9dc905e40` | Eight commits since `845aabda`: SM-P619 RIL/SMSC/UICC shims, Generic IMS, optional IPsec and a keymaster soong-config rework. Not applicable to the Wi-Fi-only product; keymaster change deferred to protect credential continuity. |
| Sevenrock vendor `lineage-24.0` | `985bd13aaa869bbcd501eb6bfc74aec17393ee1c` | T RIL blob/library swap and EGL symlink extraction metadata. No new blob versions. |
| Sevenrock kernel, gta4xlve-dev device/kernel/vendor | unchanged | — |
| Samsung SM-P613 XAR/BTU firmware | P613XXS8CYE1 | Vendor patch date still 2025-05-01; no newer blobs. |
| Lineage Gerrit `topic:C_asb_2026-12` | 1 change, NEW | "manifest: Forks for 2026-12 ASB", opened November 19. |

Of the 295 GitHub project selections, 73 moved. Most are other SoCs, TV, car
or infrastructure. Changes applicable to this build:

- Security: Chromium WebView 156.0.8078.47 → 157.0.8103.78; lineage-sdk
  privileged-caller restriction and type-checked parcel reads for profiles plus
  LiveDisplay permission enforcement; LineageParts NFC-only profile switches;
  exfatprogs 1.4.4 fsck boot-sector/cluster-count overflow validation.
- Device-used fixes: `audio.primary.atoll` battery-listener null thread join
  (hardware/qcom-caf/sm8150/audio `3ac0f60c`); recovery menu/touch/sideload
  memory; SystemUI, Launcher3 and Settings fixes.
- Build configuration: vendor/lineage now passes `TARGET_BOARD_PLATFORM` as a
  kernel make flag (moved from hardware/qcom-caf/common); shared sepolicy label
  additions.

The BPF loader, Pixel thermal and CAF sm8150 display upstreams are already
contained in our pins.

## Prepared sources

[frameworks/av](https://github.com/tylxr59/android_frameworks_av/tree/maintenance/los24-december-20261125)
`maintenance/los24-december-20261125` at `f9b499551862` merges Lineage
`965b3f762126` (DTS/AC3 extractors, MediaCodecBuffer null-backed `setRange`,
DrmHalHidl `requiresSecureDecoder` fallback) into released `a7dd9c12`. Common
base `1c5914737a1a`; no file overlap with the codec capability-owner fix
`b911f1a2e8`, which remains the only difference from Lineage. Its actual-wrapper
ASan/UBSan host regression passes on the merge.

The [device fork](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/ca4bc70f117e8c85dc1a3f5abb3fae587b13289f)
`maintenance/los24-november-20261105` at `ca4bc70f117e` removes the inherited
`vm.swappiness 145` write. The 4.14 kernel rejects values above 100, so the
release already runs at the kernel default of 60 (rooted read on 2026-11-27);
effective tuning is unchanged. This commit is newer than the first build below.

Candidate pins: [december-prep-forks-20261125.xml](../manifests/candidates/december-prep-forks-20261125.xml)
(frameworks/av and device differ from the release fork manifest) and the full
1,243-project [december-prep-20261125.xml](../manifests/candidates/december-prep-20261125.xml).
The workspace was switched from the pinned release manifest to upstream
`lineage-24.0` with this candidate local manifest; every working tree was
verified at its pin. Restore the release with the saved pre-sync manifest or
`tools/sync-source pinned` after removing the local manifest.

## Build

This is the first build on the replacement host (fresh `out/`). The exact
candidate pins were verified before compilation. `target-files-package`,
`recoveryimage` and `check-vintf-all` completed successfully in 5h47m40s:
four jobs under a 12-CPU quota, nice 19, IOWeight 50, MemoryHigh 30 GiB and
MemoryMax 40 GiB, with no OOM (cgroup peak about 32 GiB). Soong does not pass
`GOMEMLIMIT` through, so the cgroup was the only memory bound.

- Strict combined VINTF result COMPATIBLE against actual kernel inputs
  (`4.14.357-openela-perf-gbe84fa84d820`, generated kernel config). The isolated
  system pass logs three "Cannot resolve path /vendor/manifest.xml" probes for
  the legacy path; they are not compatibility failures.
- `tools/verify-kernel-btf.py` passed with `clang-r596125` (the compiler recorded
  in vmlinux): actual linker boundaries, 171,874 types within consumer limits,
  unique `seq_file` and matching iterator/helper IDs.
- Properties stay `ro.build.version.security_patch=2026-11-01` and vendor
  `2025-05-01`; the packaged WebView is the 157 prebuilt.
- DTBO payload is byte-identical to release 1793916221. The kernel Image has an
  identical embedded config, toolchain and source revision but different bytes.
  The fresh output directory generated a new `certs/signing_key.pem` module
  signing key, and the build counter and date differ. Incremental builds in the
  earlier workspace reused that key, so earlier "kernel identical" statements do
  not carry over to this host. Treat the kernel as new bytes requiring boot,
  BPF and accounting checks.

This build is unsigned and was not installed. Signing with the existing 47
identities and every device check remain for the December candidate.

## Next steps

When the December series and patch-date change merge, re-sync with the candidate
fork pins, review the December bulletin's kernel and Qualcomm entries against
the legacy kernel, rebuild, then follow the signing, no-wipe install and
validation runbook. If December slips past mid-month, consider shipping this
merged state for the WebView and lineage-sdk fixes.
