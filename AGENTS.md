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
source: device `12c0e2d`, kernel `88b63b7ae`, vendor `4388d72`. Current public
release is `1792851872`; its exact candidate manifest is retained separately.
Earlier clean bootstrap and same-key Android Updater local installs retained the
original unlock pattern, setup and saved data. Keep hardware/local-install
proof separate from advertised public HTTPS OTA download/install evidence.
`manifests/gta4xlveu.xml` pins the three device-specific forks for upstream sync.
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


## Current maintenance release

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
