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
`manifests/known-good.xml` pins the tested prototype; `manifests/resolved.xml`
pins the current candidate, which adds the project OTA URL. Do not call the
candidate hardware-tested merely because the earlier prototype booted.
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
See docs/ota.md for one-time signing/bootstrap work still required.

Creating this public source/docs repo was authorized. Publishing a ROM was
previously prohibited and is **not authorized by that alone**. An explicit
request to ship/push a ROM update authorizes that release after validation.
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

No public ROM has been published yet. First release-key generation/signing,
key migration/bootstrap, and end-to-end in-Android OTA remain to be completed.
Do not turn an empty-feed connectivity test into a claim of verified OTA install.
