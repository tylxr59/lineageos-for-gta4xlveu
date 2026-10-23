# Agent instructions

## Goal and repository boundaries

Maintain an ordinary unofficial LineageOS installation for **SM-P613 / gta4xlveu**.
A request such as “get us up to date with mainline LineageOS and push an update”
means carry the process through upstream review, source fixes, reproducible
build, release signing, validation, and publication of a working OTA. Follow
[docs/maintenance.md](docs/maintenance.md); report material blockers candidly.
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
source: device `4c68bc9`, kernel `75a416868`, vendor `4388d72`. Clean bootstrap
and a subsequent same-key Android Updater local install passed, retaining the
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
are not release candidates. The current feed is intentionally empty until an
approved, signed, tested release exists. Never advertise nonexistent/draft assets.

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

Run `python3 -m unittest discover -s tests -v`, `tools/ota.py validate ota/gta4xlveu.json`, and shell syntax checks after tooling changes.
Test security-sensitive metadata failure cases. Build source changes in the
real Android environment. Record build, manifest, hashes, signing identity,
recovery status, full image readback, boot completion/encryption/SELinux, and
actual hardware evidence as applicable. Distinguish source checks, successful
compilation, recovery boot, Android boot, and hardware functionality.

No public ROM has been published yet. Private-key bootstrap and a subsequent
same-key Android Updater local install passed. The Gatekeeper credential-unlock
defect was fixed by including the existing narrow tee rules in vendor policy
(device `4c68bc9`); retain that fix and the four boot fixes. The final tested
build timestamp is `1792775790`, release-keys, FBE, SELinux enforcing, normal
ADB UID2000, Rooted debugging disabled, empty crash buffer, original pattern/
setup/test file retained. Owner hardware smoke passed for Wi-Fi, both cameras,
speakers and S Pen. See docs/testing.md for hashes and remaining tests.
An actual advertised public HTTPS OTA download/install remains untested. Do not
turn the successful local Updater installation or empty-feed check into that claim.
