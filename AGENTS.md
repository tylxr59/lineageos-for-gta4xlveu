# Agent instructions

## Goal and repository boundaries

Maintain an ordinary unofficial LineageOS installation for **SM-P613 / gta4xlveu**.
A request such as “get us up to date with mainline LineageOS and push an update”
means carry the process through upstream review, source fixes, reproducible
build, release signing, validation, and publication of a working OTA. Follow
[docs/maintenance.md](docs/maintenance.md); report material blockers candidly.
For **“check/look for updates”**, start with the exact repository/branch map and
fetch/compare procedure in [docs/maintenance.md](docs/maintenance.md#start-here-request-scope-and-update-sources).
Report the delta against released manifest pins; do not install or publish from
an audit-only request. Check both the LOS24 platform and shared Qualcomm kernel
base (historically `lineage-20`), plus the Sevenrock/gta4xlve-dev device forks.
The dated [source audit](docs/source-upstream-audit.md) records the last reviewed
kernel base; refresh live heads rather than assuming it is still current.

Do not silently change the supported device, add app-root tooling or GApps,
relax SELinux, or drop compatibility checks to get a build through.

README is for users. Keep agent/build details here and under docs/. Document
current facts without copying chat logs, stale handoffs, private host topology,
or app inventories. Record findings in docs/port-findings.md and test evidence
in docs/testing.md. Update manifests when sources change. Imported upstream
branches should remain intact; use maintained work branches in the source forks.

## Source and build state

Read docs/building.md, docs/port-findings.md, docs/testing.md, and docs/ota.md first.
`manifests/known-good.xml` retains the earlier tested development prototype;
`manifests/resolved.xml` pins the current privately signed, hardware-tested
source: device `038bb20`, kernel `dc07aa16f`, vendor `1c0a6f2`, Pixel `d4f83b6`.
Current public release is **1792961358**, with matching resolved/fork pins and feed.
Earlier clean bootstrap and same-key Android Updater local installs retained the
original unlock pattern, setup and saved data. Keep hardware/local-install
proof separate from advertised public HTTPS OTA download/install evidence.
`manifests/gta4xlveu.xml` pins four maintained forks, including the Pixel thermal HAL.
Platform source updates and Android major-version migrations are separate risk
levels: review compatibility and installation/signing implications explicitly.

Use the existing Android checkout and incremental outputs when available.
Determine the actual workspace and read applicable parent AGENTS.md. On the
original host, this public checkout is inside the existing build workspace;
its private sibling checkout/history, Android sources, rootless Ubuntu, logs,
and artifacts were deliberately retained. Do not resync hundreds of projects
or relocate the checkout just because this public repository is small.
Inspect OS, CPU/RAM/swap, free space and package tools before setup/sync.
The existing rootless Ubuntu 24.04 wrapper is documented in docs/building.md.
Keep generated sources, logs, archives, and keys in ignored local directories.
Do not create paid cloud resources or upload proprietary/private local data.

## OTA and signing

LOS24 Updater consumes a **v2 JSON array**, not the old `response` object.
The ROM sets `lineage.updater.uri` to this repo’s HTTPS raw ota/gta4xlveu.json.
Full packages are required for this non-A/B device; recovery performs installation.
Keep this release channel on stable private signing keys. Public test-key builds
are not release candidates. The live feed advertises approved, signed releases. Never advertise nonexistent/draft assets.

Use tools/ota.py to prepare/validate metadata; it never publishes. Pin the
release certificate in ota/release-cert.sha256 before the first public build.
Use tools/publish-update only when publication is authorized; it publishes the
release assets before pushing the feed. Do not regenerate signing keys between
builds. Keys must stay outside Git and have a separate owner-held backup.
Persistent keys are already initialized and pinned. Read docs/signing.md before
using them; restore the existing owner backup on a new builder, never generate a
replacement release identity. The current inventory has 47 private identities.

The owner explicitly authorized the first full public release on 2026-10-23
after successful signed bootstrap/local-update tests. An explicit request to
ship/push a ROM update authorizes release publication after validation. Source
repo creation alone does not authorize an otherwise unrequested ROM release.
Tablet modification permission applies only to the owner’s tablet and existing
session authorization. Otherwise use read-only ADB unless authorized. Never
wipe personal data as an ordinary update step. Do not collect device identifiers
or personal data; redact local logs before showing excerpts.

## Verification and completion

Read [docs/vintf-audit.md](docs/vintf-audit.md) before kernel compatibility work.
The previous release `1792787032` had an OTA kernel-check bypass hiding missing
toolchain-reporting symbols and disabled kernel CFI. The current release fixes
both and restores strict kernel checks. Separately pushed candidate branches
`fix/los24-vintf-cfi` provide genuine detection, enforcing CFI and restored checks;
build1792849929 passed signed no-wipe installation, Android/recovery boot,
original pattern/data persistence and owner hardware smoke checks. See the audit
for exact revisions/evidence. Combined candidate `1792851872` uses device
`12c0e2d`, kernel `88b63b7ae` (shared Lineage base `285869032`), and vendor
`4388d72`, with current platform changes. Its separate resolved manifest is
`manifests/candidates/maintenance-20261024.xml`. Signed no-wipe Android boot,
owner hardware smoke checks, recovery partition verification and a final
recovery-menu Android return with pattern/data persistence all passed. The owner
then authorized publication; build `1792851872` is now the current public release
with matching source pins and OTA feed. Host-only edited
diagnostic configs are not a fix. Keep this separate from AVB and paused audio.

Run `python3 -m unittest discover -s tests -v`, `tools/ota.py validate ota/gta4xlveu.json`, and shell syntax checks after tooling changes.
Test security-sensitive metadata failure cases. Build source changes in the
real Android environment. Record build, manifest, hashes, signing identity,
recovery status, full image readback, boot completion/encryption/SELinux, and
actual hardware evidence as applicable. Distinguish source checks, successful
compilation, recovery boot, Android boot, and hardware functionality.

The first full public ROM release and v2 feed entry are published (tag
`lineage-24.0-20261023-gta4xlveu-1792775790`). Private-key bootstrap and a subsequent
same-key Android Updater local install passed. The Gatekeeper credential-unlock
defect was fixed by including the existing narrow tee rules in vendor policy
(device `4c68bc9`); retain that fix and the four boot fixes. The first release’s tested
build timestamp was `1792775790`, release-keys, FBE, SELinux enforcing, normal
ADB UID2000, Rooted debugging disabled, empty crash buffer, original pattern/
setup/test file retained. Owner hardware smoke passed for Wi-Fi, both cameras,
speakers and S Pen. See docs/testing.md for hashes and remaining tests.
Public HTTPS Updater detection, download, signature verification, recovery
installation and boot passed from timestamp1792775285 to1792775790 with no wipe.
The original pattern/setup/test file persisted; FBE, enforcing SELinux, normal
ADB, disabled Rooted debugging and empty crash buffer were verified. The exact
released recovery/vbmeta pair was boot-tested and fully hash/trust-checked.


## Wi-Fi tablet / UI follow-up

Device `eb9bc69` switches SM-P613 to the Wi-Fi-only tablet product, sets tablet
characteristics, removes the incorrect IMS declaration and bundled Phone,
Contacts, Messaging and SIM Toolkit apps, and overlays SystemUI lock-icon padding
to 24dp. Keep Android's shared providers/picker and Qualcomm vendor components;
the removed launcher apps do not require stripping shared APIs or LTE-SKU blobs.
Native density remains 240dpi. The Clock widget still needs sufficient row height.

Signed build1792785825 passed a no-wipe recovery sideload, Android boot, original
pattern/setup/test-file persistence, FBE, enforcing SELinux, normal UID2000,
Rooted debugging off and an empty crash buffer. Owner confirmed normal lock-icon
appearance and Wi-Fi/both cameras/speakers/S Pen operation. The newer same-source
build1792787032 was published as the [Wi-Fi tablet update](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261023-gta4xlveu-1792787032). Actual advertised
HTTPS Updater detection/download/signature verification/recovery installation
and Android boot passed from1792785825 to1792787032 without a wipe. Encrypted
data unlocked, setup flags and the saved-file checksum persisted, SELinux stayed
enforcing, normal ADB/Rooted debugging off and an empty crash buffer passed.
The automatically updated release recovery booted; full boot/DTBO/recovery
partition hashes and its single live OTA trust certificate match the assets.
Ordinary OTA retained the preceding vbmeta; the new bundled vbmeta was verified
on the host. All 12 public assets and the two-entry feed were checked. The
existing 47 private signing identities and owner backup remain unchanged.

A shared-host product reconfiguration exhausted memory at higher concurrency.
The helper now defaults to four jobs. Read the demonstrated memory-budget notes
in docs/building.md; plain Go environment exports may be stripped by the build
launchers. Preserve completed outputs and verify effective executor settings.


## Previous maintenance release 1792851872

Published build `1792851872` combines genuine enforcing CFI, restored OTA kernel
checks and upstream LineageOS changes. See docs/source-upstream-audit.md for the
project delta and shared kernel base `285869032633b3de3c6bdefd8f3b553f988c11da`.
The prior two release sections above retain historical validation evidence.
Current build passed signed no-wipe installation, Android/recovery boot, exact
partition hashes, original pattern/setup/test-file persistence and owner hardware
smoke checks. All public asset sizes/digests and the HTTPS feed were verified.
The test tablet already ran this timestamp before publication: no new older-to-newer
public Updater install is claimed for this release. Earlier public Updater tests
remain valid history; distinguish them from this release's distribution checks.

A fresh download of the public ROM ZIP matched the tested bundle SHA256. The
tablet also fetched the canonical three-entry HTTPS feed successfully.


Before further hardening, read [the build/security exceptions audit](docs/build-exceptions-audit.md).
The audited1792851872 baseline disables KPTI and reports Meltdown Vulnerable,
but physical susceptibility/exploitability is unproved. That baseline also had
three BUILD_BROKEN flags and vendor ELF-check exclusions, resolved below. Do not blindly flip AVB flags,
relock the bootloader, enable root or treat boot sleep_disabled=1 as a proven
standby failure; runtime post-boot handling and access limitations are documented.


## Hardening test history (superseded by release 1792876959)

Read the follow-up in docs/build-exceptions-audit.md before changing these sources.
Historical candidate1792860066 is signed and hardware-tested: deviceb07f055, kernel0c5ccf4fc,
vendor1c0a6f2 on fix/los24-hardening. See
manifests/candidates/hardening-20261024.xml. Its fixes are included in the later
public release 1792876959; retain this earlier validation record.

KPTI requires kernel entry fix18eeda8c4: apply_ssbd clobbered NZCV later used to
select native/compat return. Both mitigations remain enabled. The candidate adds
upstream Kryo silver CPU identification; Android reports Not affected, while
matching recovery explicitly detects KPTI forced on for KASLR. Enforcing CFI,
strict VINTF, all three removed BUILD_BROKEN switches, restored vendor ELF checks,
actual dependency installation and full policy/neverallow/image checks passed.
Six unused permissive vendor test domains are removed; normal userdebug's su,
backuptool and qti-testscripts remain. Live recovery labels passed51 wakeup and3
battery checks. Full Android kernel-audit visibility was unavailable to normal
ADB; do not claim all legacy denials disappeared.

Signed no-wipe installation, owner original pattern/setup/hardware smoke checks,
matching recovery/full boot-DTBO-recovery hashes and final Android return passed.
Encryption/enforcing SELinux/normal ADB/Rooted debugging off passed, with no app-root
added. Temporary probe/test file removed; signing identity/backup unchanged.
Verification-enabled vbmeta was tested and rejected by Samsung bootloader trust;
original metadata restored. Do not repeat a flags-only AVB experiment or relock.
No newer maintained vendor blobs were found; do not fake the vendor patch date.

Boot-only diagnostic tests must account for automatic recovery updating. The
installed /vendor/etc/recovery.img can replace a manually preserved recovery
after Android boots. Verify the live partition before another recovery reboot;
prefer complete matched updates, or deliberately manage/restore Updater's recovery
update setting (persist.vendor.recovery_update). The combined candidate's vendor
recovery payload/updater target matches its signed recovery and live partition.
A pending sideload-auto-reboot request can show No command while ADB is already
in sideload mode; inspect USB/ADB state before another bootloader restore.

## Previous USB and hardening release 1792876959

Read docs/usb-mtp-audit.md before USB init changes. Release 1792876959 uses
manifest manifests/candidates/usb-mtp-20261024.xml: device02b4ef7, kernel0c5ccf4fc,
vendor1c0a6f2. Only the device project differs from the tested hardening candidate.
Normal on boot now selects HAL configfs2; charger legacy mode remains1. Shared
QTI USB stays upstream0d32cd0; maintain the existing three forks.

Signed no-wipe installation, Android/data/security checks, five mode selections,
exactly one ADB interface, automatic ADB reattachment and KDE KIO checksum copies
passed without rooted debugging. Owner physical-reconnect/Dolphin/pattern checks
also passed. Matching recovery/full partition hashes passed; original vbmeta is
unchanged. Final recovery-menu Android return, unlocked encrypted data, saved
checksums and another KDE MTP readback passed. Both owned probes were removed;
normal ADB/Rooted debugging off remain. The owner authorized publication, and
release 1792876959 is published with matching manifests and feed. All 12 public
assets and canonical HTTPS feed were verified. The tablet already ran this
timestamp; no separate older-to-newer public Updater installation is claimed.
See docs/testing.md for hashes and remaining limitations.


## Follow-up correctness/performance audit

Read docs/performance-followup-audit.md before new performance tuning. Read-only
review of release1792876959 confirmed missing framework thermal HAL feedback
while the vendor thermal engine runs, failed launch LLCC bandwidth hint writes,
and the inherited BPF kernel-version override (5.10.239 over actual4.14.357).
Prioritize truthful thermal integration and diagnosing the failed hint. Audit
BPF capabilities/backports separately; do not remove the override blindly.
DMA-BUF iterator errors have a sysfs fallback requiring validation. Old ART and
Samsung properties are cleanup leads, not proof of global AOT failure. Active
SurfaceFlinger offsets need controlled traces before changing them. Normal ADB
cannot inspect all HAL/sysfs state; shell inspection AVCs are not product bugs.
No tuning/build/install/release change was made by this follow-up audit.

Performance follow-up work is now authorized, but the owner explicitly said
**do not flash anything yet**. Do not install, flash, wipe or reboot a candidate
without renewed instruction. Device branch fix/los24-performance-followup at72a336a
contains reporting-only thermal staging, the diagnosed 8137->8136 launch-hint fix
and obsolete-property cleanup. Build pending; no hardware success claimed.
Read the latest follow-up section in docs/performance-followup-audit.md. Release
pins/feed1792876959 remain unchanged. Temporary rooted inspection was cleaned up
and normal ADB/Rooted debugging off verified. BPF override/active graphics tuning
remain, DMA-BUF fallback is confirmed absent, and newer-kernel work is only a
researched lead. Retain these limits in future claims and source reviews.


The owner later explicitly authorized flashing/testing this performance candidate
on the same evening. A signed no-wipe local update is now authorized; publishing
an OTA is not. The earlier no-flash constraint above is historical. Final device
source d61cc85 includes source-proven startup Power HAL client/config access and
scheduled IStats Binder dependencies. Full corrected build passed; signing and
runtime validation pending. See manifests/candidates/performance-followup-20261024.xml.
Public release/feed stays1792876959 until a separate shipping request.


Performance runtime update: signed candidate1792893543 (d61cc85) installed but
stalled before boot completion because framework waits for declared IThermal
before the sys.boot_completed service trigger. Do not install/publish that image.
Source f38d06f starts reporting at `on boot`; rebuilding in a separate local
artifact directory. See manifests/candidates/performance-startup-fix-20261024.xml.
Thermal startup permission queries passed using Android libsepol, but inherited
Qualcomm policy already permits thermal sysfs writes; the reporting-only boundary
is configuration/code behavior, not a full-policy write prohibition. Public feed
remains1792876959. Owner authorized no-wipe local correction/testing.


Latest tested installation is now **1792894491**, device **f38d06f**, kernel/vendor
unchanged from public1792876959. Manifest:
`manifests/candidates/performance-startup-fix-20261024.xml`. Full corrected build,
existing-key signing, signed no-wipe installation, owner pattern/setup/hardware
(including rotate and Dolphin MTP), standard thermal HAL/four readings, matching
recovery/full partition hashes and final recovery-menu Android return passed.
FBE/enforcing SELinux/normal ADB/Rooted debugging off, retained marker checksum
and empty crash buffer passed. Owned marker/Perfetto configuration/traces cleaned.
Public resolved/fork pins and feed deliberately remain release1792876959; this
local test authorization does not authorize publication. Earlier1792893543 is
rejected for the startup cycle. No general launch-speed or battery gain claimed;
headroom/skin calibration, BPF capabilities, DMA-BUF and graphics work remain.


The owner has now explicitly requested publication of tested1792894491. Release
preparation pins resolved/fork manifests to devicef38d06f (kernel/vendor unchanged).
The exact signed local-test bundle is being packaged; live feed remains1792876959
until all release assets upload successfully. Do not rebuild or publish rejected
1792893543. Check actual release/feed state and local publish progress before
retrying any publication command.


## Published thermal and launch-hint release1792894491

The owner authorized publication. [Release1792894491](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792894491) now includes the
exact signed/hardware-tested local candidate; resolved/fork manifests and live
feed match devicef38d06f, kernel0c5ccf4fc, vendor1c0a6f2. All12 public asset sizes/
SHA256 digests, downloaded checksums/ROM and canonical five-entry HTTPS feed from
both host and tablet matched. The tablet already ran this timestamp; no new
older-to-newer public Updater installation is claimed. Earlier local no-wipe,
owner hardware/pattern/data and matching recovery/full partition hashes passed.
No new keys, logger or app-root. Rooted debugging remains off. See testing and
performance audit for limits, including no demonstrated speed/battery gain.
The earlier no-publication sections above record historical authorization states.


Before log cleanup or further thermal/audio changes, read docs/runtime-log-audit.md.
Read-only release1792894491 capture found no current crash/ANR/watchdog/AVC, but
identified TYPE_SKIN empty-threshold queries incorrectly throwing EX_ILLEGAL_STATE
in Pixel thermal helper. CPU/GPU/battery still work. Do not fake SKIN data to hide
it. TI IV-width/VBAT module0x1000fc00 rejection persists from the paused audio
investigation; DMA-BUF iterator and fallback remain absent. Historical22:13–22:24
watchdog DropBox entries belong to rejected1792893543, not the current boot.
No device/source/OTA changes made by this audit; raw logs stay private.


Current runtime follow-up: read docs/runtime-fixes.md and CHANGES.md. Installed
signed candidate1792933707 is NOT public; release/feed still1792894491. New fourth
fork tylxr59/android_hardware_google_pixel, fix/los24-thermal-empty-queries,
d4f83b6 based on released8bd3c71. All11 native tests, clean full ROM/strict VINTF,
persistent-key signatures, no-wipe sideload, owner pattern/setup/hardware tests,
live thermal queries, matching recovery/full partition hashes and recovery-menu
Android return passed. Only the Pixel project changes from the released resolved
manifest; kernel/DTBO identical, original vbmeta unchanged. No thermal query
exceptions or crashes observed, no fabricated skin/cooling. Rooted debugging off,
UID2000, temporary native tests and data marker removed. See candidate manifests
runtime-fixes-20261025.xml and runtime-fixes-forks-20261025.xml. Workspace local
manifest selects this candidate; preserve before any sync-source overwrite.

The isolated kernel branch wip/los24-dmabuf-iterator at423e21526 adds optional
DMA-BUF iteration plus BTF host-tool repairs bbac598e2 and conditional ID fix
2756333ec. Two Image builds passed, including source-integrated host tooling;
duplicate-name regression/missing-BTF negative tests passed. BTF kinds1–15 and
DMA-BUF ID verified. Default-off, NOT in installed thermal ROM or release pins.
No kernel boot, CO-RE loader, accounting/stress/suspend/performance proof yet.
TI audio source review found unowned-mux cleanup risk in the saved prototype;
no live audio changes. Keep factory calibration/gain/protection untouched.
User overnight report100→97 included30minYouTube; exact duration not supplied,
no measured suspend/energy proof or ROM battery-gain claim.

Maintain CHANGES.md with links to implementation commits in the relevant forks
and project tooling. Keep uninstalled work under Unreleased; promote entries only
after the release runbook checks. Do not list experiments as shipped fixes.

DMA-BUF follow-up active: read docs/dmabuf-accounting.md. Kernel candidate branch
fix/los24-dmabuf-candidate at1d5531f9a adds legacy reader resume/close repair52847c63d,
device BTF/iterator enable0618060fb, host ASan/UBSan lifecycle harness40dd1806a,
and Android-sandbox LLVM host-tool selection1d5531f9a. Host actual-source tests
and all9 Android-object field relocations passed; device loader/accounting/race
proof pending. Candidate manifests dmabuf-20261025.xml and dmabuf-forks-20261025.xml
change only the kernel from locally tested thermal1792933707. Public release
manifests/feed remain1792894491. Do not reinstall the earlier iterator prototype:
it can truncate output at legacy read boundaries. Main workspace kernel checkout
now selects this candidate; preserve before syncing. No audio source changes.

DMA-BUF candidate1792935924 atkernel1d5531f9a is REJECTED: full ROM/host checks
passed, no-wipe sideload succeeded, owner reported bootloop before Android.
Do not reinstall/publish unchanged. Known thermal1792933707 recovery restored
only; collect pstore before any system boot, then restore full known signed ROM.
Do not boot mismatched restored recovery/new vendor recovery payload without
restoring the full ROM. Public feed remains unchanged. See dmabuf-accounting.md.

Follow-up BTF diagnosis: failed-boot pstore says hdr_len not found, then kernel
BTF malformed in critical NetBpfLoad. Parser used obsolete weak binary symbols
(undefined/zero), while linker/sysfs use __start_BTF/__stop_BTF. Fix4823beeb2
aligns consumers. Review also found16-bit type/name limits insufficient for full
vmlinux; fix8861e8c76 matches pinned Android UAPI20/24-bit limits and propagates
btf_add_type allocation failure. Supported kinds unchanged. Symbol-only build
stopped before install. Corrected full ROM rebuilding from8861e8c76; not tested.
Full working1792933707 rollback boot/data/security was verified, rootdebugOFF.
Keep rejected1792935924 evidence, do not overwrite/reinstall. Preserve local
candidate pins; public release/feed remain1792894491. No audio work resumed.

Parser-only8861e8c76 bundle passed full build/BTF boundary+limits/sign checks but
was superseded BEFORE install. Review traced duplicated seq_file BTF through
perf_event.rb to perf/trace both using tag ring_buffer. Backport4c536a5bc of Linux
56de4e8f9146 renames only perf tag in4files/64occurrences; no fields/statements/
function names change. New guard requires unique seq_file and equal iterator
metadata/typed-helper IDs; rejects pre-rename blob. Latest kernel candidate
branchfix/los24-dmabuf-candidate now4c536a5bc; full ROM pipeline active separately.
No device test yet for these repairs. Preserve rejected1d/1792935924, never flash
it. Last verified installed remains thermal1792933707 with data/security intact.

Use tools/verify-kernel-btf.py for every BTF-enabled kernel build before install.
It checks actual object/ELF symbols, generated BTF against consumer limits, unique
seq_file and actual iterator/helper BTF ID equality. Positive actual-kernel and
negative obsolete-ELF checks passed; negative check still rejects under python-O.
See dmabuf-accounting.md for invocation. Real boot/accounting tests still required.


DMA-BUF newest checkpoint (2026-10-25): earlier candidate notes above are history.
Signed1792944959 / kerneldc07aa16fd2eb4be6dea6a9a14d3385bcb663d3a is now installed
and has working pinned iterator/accounting. Branch fix/los24-dmabuf-candidate
(and fix/los24-dmabuf-jit) is pushed. Sources are candidate manifests
dmabuf-jit-20261025.xml and dmabuf-jit-forks-20261025.xml, including Pixel thermal
fixd4f83b6, devicef38d06f/vendor1c0a6f2 unchanged. Do not sync back to released
three-fork pins without preserving this candidate. Public release/feed remain
1792894491; no new publication requested. Read docs/dmabuf-accounting.md.

The final ARM64 repair adapts upstream exception-table handling282b0b486 and
user-address guardecf66a6f9, with actual-source host testsdc07aa16f. Full signed
ROM/VINTF/BTF checks passed, no-wipe boot/data/security passed, live1024-buffer
probe at1/17/4096/65536-byte chunks returned all owned inodes exactly once, ten
concurrent scans/2667allocation-free ops and200early-close owned-resume tests
passed with no owned buffers retained. Six accounting snapshots, live BTF/ELF
equality, user-space perf functionality and no new observed faults/crashes passed.
Owner confirmed pattern/setup, video, Wi-Fi, both cameras, speakers, S Pen,
auto-rotate and File Transfer. No induced ARM64 data-abort test, long endurance,
energy/memory reduction or blanket modern-BPF compatibility claim.

Temporary probe removed; Rooted debugging disabled through official service and
UID2000/settingfalse verified. Matching recovery/kernel/config and full boot/DTBO/
recovery partition hashes passed; old vbmeta unchanged. Final recovery-menu Android return and
owner unlock, data-marker persistence/security checks passed. Owned marker and
temporary helpers removed; Rooted debugging off/UID2000 verified. Local evidence stays private
under artifacts/dmabuf-jit-candidate-20261025/. Do not publish raw logs/helpers.
TI audio remains paused; no factory calibration/gain/protection changes.


Owner explicitly authorized publication of tested1792944959. Exact tested bundle
is prepared under artifacts/dmabuf-release-20261025. Pins prepared; live feed
stays1792894491 until successful upload. Kernel upstream hint corrected to
fix/los24-dmabuf-candidate without changing any revision. Inspect actual remote
release/feed before retrying publication.


## Published DMA-BUF and thermal-query release1792944959

Owner authorized publication. [Release1792944959](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261025-gta4xlveu-1792944959) publishes the exact
signed, locally installed/tested bundle, ROM SHA256
b4805ab09c75b65b4157a34bec6e1919e5a1d8593a8008cf657f0ac1c2f6b6ee.
All12 public asset sizes/SHA256 digests, downloaded ROM/checksums and canonical
six-entry HTTPS feed on host/tablet passed. Only kernel and Pixel HAL differ
from1792894491 among all1242project pins. Kernel upstream hint now correctly
names fix/los24-dmabuf-candidate; revision unchanged. Four maintained forks are
needed, including Pixel fix/los24-thermal-empty-queries. Update-source map and
building guide record them. Do not sync using the old three-fork manifest.

Tablet already ran1792944959, so no additional older-to-newer public Updater
install is claimed. Signed local no-wipe update, pinned iterator/live bounded
probe, owner hardware/pattern/data checks and matching recovery round trip passed
as documented above. Final boot/UID2000/rootdebugfalse checks passed. Existing
keys/rollback assets unchanged; no app-root/logger/audio experiments included.
Earlier no-publication/pending statements are historical. See CHANGES/testing.


## Active Bluetooth media fix (2026-10-25)

Owner's first real AirPods Pro2 audio test exposed connected A2DP/AAC but no
media route: policy rejects adding A2DP, output stays on speakers. Read
docs/bluetooth-audio.md. Device branch fix/los24-bluetooth-audio at038bb20 adds
AOSP android.hardware.bluetooth.audio-impl + automatic VINTF fragment. Existing
audio service loads it; legacy session utilities already bridge AIDL. No root
enabled or device settings changed during diagnosis. Full signed pipeline
los24-bluetooth-candidate.service active; logs/bluetooth-airpods-build.log and
artifacts/bluetooth-airpods-20261025/progress.json are actual state. No automatic
installation in pipeline. Follow signing/host/no-wipe/audio tests before claiming
fix. Current installed/public release1792944959 and livefeed unchanged; no new
publication request. Local manifest selects candidate device038bb20, preserves
kerneldc07aa16f/Pixeld4f83b6/vendor1c0a6f2. TI audio remains paused.


Bluetooth candidate1792961358 is now installed and locally complete, superseding
the earlier build-pending checkpoint. Device038bb20 only changed project among
1242pins vs1792944959; kernel/DTBO/boot identical, Pixel/vendor unchanged. Full
build/strictVINTF/BTF/existing-key signing/no-wipe install passed. Real AIDL
provider registered; A2DP route available. Owner confirmed AirPodsPro2 AAC audio,
speaker fallback, independent volume and reconnect playback. Standard software
A2DP start/suspend passed; no original route errors/new observed audio AVCs or
crashes. No SCO mic/other headset/codec/endurance proof. No root ever enabled.
Matching recovery/full boot/DTBO/recovery hashes and final Android unlock/data/
setup/security/cleanup passed; old vbmeta unchanged. Owned Bluetooth marker
removed. Evidence artifacts/bluetooth-airpods-20261025/progress.json. Local
manifest selects device038bb20; preserve candidate before sync. Public released
manifests/feed stay1792944959 until separate release request. Read Bluetooth doc.


Owner authorized publishing tested Bluetooth candidate1792961358. Exact tested
bundle prepared under artifacts/bluetooth-release-20261025; source pins prepared,
live feed remains1792944959 until successful asset upload. Preserve releases
and inspect actual remote state before retrying publisher.


## Published Bluetooth media release1792961358

Owner authorized publication. [Release1792961358](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261025-gta4xlveu-1792961358) contains the exact
signed installed/tested ROM, SHA256
422a5e58b584c5855b6d66683763b8387efae0ae32ecb201a90fc0d025e9bef6.
All12 public asset sizes/GitHubSHA256, freshly downloaded ROM/checksums and
canonical seven-entry HTTPS feed on host/tablet passed. All1242source pins
compared with prior1792944959: only device038bb20 differs. Four maintained
forks retained; device branch now fix/los24-bluetooth-audio. Full no-wipe local
install, owner AirPods AAC/speaker fallback/volume/reconnect, recovery/full
partition hashes and final Android/data/security checks passed as documented.
Final provider/boot/UID2000/rootdebugOFF checks passed. Existing keys/backups and
rollback releases unchanged. No new public older-to-newer Updater install was
repeated because tablet already ran this exact timestamp. No fresh vbmeta flash,
SCO mic/other-headset/codec/endurance proof. Earlier pending/no-publication notes
are historical. See Bluetooth findings, testing and CHANGES for implementation.
