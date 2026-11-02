# November 2026 update readiness

Checked November 2, 2026 against released build **1793279242** and its
1,242-project resolved manifest. This was a source audit: fetches and merge-tree
previews only; no source checkout sync, working-branch merge, build, install or
publication. The tablet was unavailable to ADB, so installed state comes from
the completed October 29 validation record, not a fresh device observation.

## Decision

Routine merged LineageOS updates are candidates for integration, with clean Git
merge previews. A complete November security update is **not yet established**.
Wait for the November security series to land, refresh the comparison, then build
and validate a combined maintenance candidate. Do not advance the security patch
property merely because the bulletin has been published.

## November security status

The [November bulletin](https://source.android.com/docs/security/bulletin/2026/2026-11-01)
was published November 2. Google says corresponding AOSP patches will be released
within 48 hours and the bulletin updated with links. Publication of the bulletin
alone does not establish patch availability or coverage in our source.

The live merged LineageOS platform manifest remains
`b51a0c449a3279ca55fb6d4d91d2143e42e2fff5`, selecting AOSP
`android-17.0.0_r1`. Its manifest files are unchanged from our release, including
the selections for the 952 AOSP projects. Those fixed-tag projects were not
individually fetched. All 287 GitHub project selections in the upstream manifest
were queried, including the three projects overridden by our platform forks.

[LineageOS change 508068](https://review.lineageos.org/c/LineageOS/android/+/508068),
“manifest: Forks for 2026-11 ASB”, is NEW, patch set 5,
`07b127aa2f1f4df338098f70b19efc7adba2e7a2`, needing Verified and Code-Review.
It adds Lineage forks for AAC, hplip, libopenapv, tremolo, ManagedProvisioning,
IntentResolver, NeuralNetworks, Profiling, Iwlan and trusty/user/base. The
`C_asb_2026-11` topic query returned only this manifest change at audit time;
it is preparation, not evidence that the complete security fixes are merged.

The current vendor/lineage release configuration still advertises **2026-10-01**,
and the full API version remains **37.0**. Build/make, the AOSP build/release
selection and Connectivity have no new selected revision. Thus these merged
updates do not newly activate Connectivity's existing API37.1/kernel5.15 gate.
Recheck after the security series lands; do not raise the kernel override to
satisfy a future gate without capability validation.

A full November security review must separately map the bulletin's kernel and
Qualcomm issues to this backported 4.14 tree and proprietary components. This
audit does not certify CVE coverage or a November 5 patch level.

## Merged platform delta

There are **91 incoming commits across 44 project paths**, including translations,
other-device code and five Lineage infrastructure/documentation projects. All
44 have clean merge-tree previews against the corresponding released pin.
A clean preview establishes textual integration only, not build or runtime safety.

Relevant changes include framework dream/doze wake behavior, dialog styling,
button-action fixes with matching lineage-sdk/LineageParts changes, Settings
hotspot capability handling, LatinIME inline autofill/clipboard suggestions and
number gestures, Canvas undo/redo, Updater's default HTTP user agent, recovery
fill rendering, and vendor/lineage kernel make-flag propagation/include ordering.
The kernel build changes should be integrated together and checked with our
actual CFI/toolchain configuration. Many telephony, automotive, TV and newer
Qualcomm platform changes do not affect this Wi-Fi tablet's built components.

Our frameworks/av `b911f1a`, system/bpf `c2621ec` and Pixel `d4f83b6` pins contain
the respective current Lineage upstream heads, with no incoming commits.
Preserve these fork pins and their codec ownership, FUSE capability and thermal
query fixes.

## Device, kernel and blobs

Sevenrock device head is `845aabda084e161fdd42a8f8162a5c58623fb718`.
Patch-equivalence filtering leaves nine incoming commits, but several are
functional equivalents of existing repairs: vendor/etc ueventd placement,
Gatekeeper storage access, legacy ion, fastbootd and namespaces. The Bluetooth
AIDL conversion overlaps our tested AIDL-provider repair. Its health/charger
AIDL migration, recovery health service and partition-path cleanup need separate
review and hardware validation rather than automatic inclusion in a security
update. A full merge conflicts in device.mk, VINTF manifest, deleted legacy USB
init and tee policy. Preserve our USB HAL ownership, credential policy, Wi-Fi
product, thermal reporting, assisted GPS and strict VINTF checks. Do not resume
the paused TI work.

Sevenrock kernel head is `ef3c0a5dd63453bcc85e67b6a9feae17c3c8808b`.
Its shared-base merge reaches exactly the already integrated Qualcomm base
`285869032633b3de3c6bdefd8f3b553f988c11da`; the live shared `lineage-20` head is
still that SHA. Its only additional effective change removes the tablet's
`disp_rdump_memory` overlay. A clean merge preview changes only five lines in
one display DTS file, retaining our OOM/CFI/hardening changes. This restores the
inherited reserved-memory range; review compiled DTBO/layout and boot/display
behavior before inclusion. It is not evidence of new November kernel fixes.

The gta4xlve-dev device/kernel/vendor selected branches contain no incoming
commits. Both vendor upstreams remain
`4388d72aed64812cf27496986bcf8fb3af64bf1d`; retain our assisted GPS vendor changes.
Official [XAR](https://doc.samsungmobile.com/SM-P613/023882220819/eng.html) and
[BTU](https://doc.samsungmobile.com/SM-P613/023399220804/eng.html) histories still
list P613XXS8CYE1 with vendor patch date **2025-05-01**. No newer SM-P613 blobs
were identified from these sources. Platform updates cannot establish current
closed-source vendor security coverage.

## Candidate validation

After upstream security integration, capture exact candidate pins and compare
all selected project revisions again. Use the existing build checkout and signing
identity. Verify full API/kernel admission, strict VINTF, policy and neverallows,
BTF, CFI, signed OTA and paired recovery payload. Test signed no-wipe upgrade,
original credential/encrypted data continuity, normal Android and recovery boot,
USB/MTP, Bluetooth audio, cameras, speakers, S Pen, thermal reporting, assisted
GPS persistence and the retained BPF/OOM behavior. Keep public feed and release
manifests on the validated October 29 release until a new candidate passes.

## Exact incoming platform heads

- `bootable/recovery`: `c1ccd0b4a17557f97ed864b96f160674609c1c54`
- `frameworks/base`: `03e13d72d00d80eeba4465893dfad669e3ad3ce6`
- `packages/apps/Car/Settings`: `9a3e6784c0424f33e727f60af6f27a605f9abd40`
- `packages/apps/Dialer`: `3b9a8e35d2bc2c804ee1c64f9b291630a00e333d`
- `packages/apps/Launcher3`: `1402f510b49302d64e2c290e4855668e8ed48299`
- `packages/apps/Messaging`: `47eb88d3219eea82905f844baa9240925329ab6f`
- `packages/apps/Settings`: `1f24cca340897c881b9c1544b0a9d207fbff1228`
- `packages/apps/ThemePicker`: `40d1119d4150d539699a3fb8cd5df4d8f515c142`
- `packages/apps/TvSettings`: `70a89f8af02ce699ce8d3fab35d0f498174c9063`
- `packages/inputmethods/LatinIME`: `072efed63fcb6bc28650abb629b592820b2d918d`
- `device/lineage/sepolicy`: `a29110ed8d2933c8f0da9c6ff613c4b68b7e4ad8`
- `hardware/lineage/compat`: `f67ba754d88da06b73682a5e06f2e516dc2f37b7`
- `hardware/lineage/generic-ims`: `12db0c061efb08f9ea477a71d5d866c80771150f`
- `hardware/lineage/interfaces`: `68dca0c523594fb7c34e94782d0f21660530a2dc`
- `lineage-sdk`: `854d7bfc24669e18e9a318e480d573703511237b`
- `packages/apps/Aperture`: `95b12f14e7e071e0119c969db38b04d197af9e3b`
- `packages/apps/AudioFX`: `f7e26b30cc4410c537bf87248e8f0089f3355be1`
- `packages/apps/Canvas`: `0ade20ab9bee7176b9ccb9253767db31f7a24ede`
- `packages/apps/Catapult`: `5cc047c135c2c0cd8e025e5052068c12c29bd590`
- `packages/apps/DeskClock`: `bab0cdeafd94c39d98aea553947782b9c68c5e53`
- `packages/apps/ExactCalculator`: `f76cfbe2428de5744c0e0c4b74fb77708fb15b95`
- `packages/apps/Glimpse`: `5fb6f2db3be8c0b8fe9e725d56fa3251e34e18b9`
- `packages/apps/Jelly`: `604fa77181699759290105c53c40557e478dc5f5`
- `packages/apps/LineageParts`: `b9bf232ca06f34368356c9e46613bfb24076b6cf`
- `packages/apps/SetupWizard`: `9c75b8a75bb3e48d4ec96375fba00b1e409c8763`
- `packages/apps/Twelve`: `f701f1f3cecf1f0ebdf89a1e6facd1bc9b35508e`
- `packages/apps/Updater`: `1041e4c124fa0521fd7839f12f2f1113e40d1f3a`
- `packages/resources/devicesettings`: `a33069c8758e8601fb4a53f1aceac1d632c686d2`
- `vendor/apn`: `7693bb941534e2844165357dac68e6146d0b065b`
- `vendor/crowdin`: `9c0293f2f155a28e396a85b79a0c07a4279642df`
- `vendor/lineage`: `ccd59732102f741755f801ca922208e41d4c0bb3`
- `device/qcom/sepolicy`: `a8385f33b31aac5ba7f001413f4d67c7c9bf632e`
- `device/qcom/sepolicy_vndr/legacy-um`: `d8b5ffdf51074f0931096991d9e9a9294ad31c98`
- `device/qcom/sepolicy_vndr/sm8750`: `b25101da34353112dc674d73ec3a8df2cdfcde18`
- `device/qcom/sepolicy_vndr/sm8850`: `520af592e4b13685e241f3f99b9b74d7a5f87e21`
- `hardware/qcom-caf/sm8450/audio/pal`: `2b80768e69510139ecd3cbb69b61c7414e3cc0ff`
- `hardware/qcom-caf/sm8650/display`: `266bec6b1684e52530f84ab12510723a30953e29`
- `hardware/qcom-caf/sm8750/display/hal`: `5b970807ee568f53d8c9c17dae1202059c9fafc3`
- `hardware/qcom-caf/thermal`: `e2ff2bbb4a90503f88d2caa103fb6ed483601043`
- `lineage/charter`: `1e4201d9976ef9c73407830a9e9c2c990182fff6`
- `lineage/hudson`: `005676739fd64660f3ea029c0d8b38c3d55db477`
- `lineage/mirror`: `3c167eb2ffcb77ab862702d2d9c859ba41472685`
- `lineage/wiki`: `bf49224b3a8838ad67f42e014435d5feeae5a668`
- `lineage/scripts`: `abe932a7a4848f2783d9385d816fc14221287944`
