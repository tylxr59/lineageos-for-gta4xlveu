# LineageOS for Galaxy Tab S6 Lite (2022 Wi-Fi)

Unofficial **LineageOS 24.0 / Android 17** for the Samsung **SM-P613**, codename
**gta4xlveu**. Based on Sevenrock’s port and gta4xlve-dev / danielml3’s work.

**Status:** boots on an SM-P613. Encrypted data, SELinux enforcing, USB debugging,
USB file transfer and charging have been checked. Wi-Fi, front/rear cameras,
speakers, and S Pen writing/hover passed owner smoke tests. See [tested features](docs/testing.md)
for what remains unverified.

This repository holds installation guidance, reproducible source manifests,
and the update feed. The device, kernel, and vendor sources live in the
[linked forks](docs/building.md#sources).

## Downloads

**[Download the 2026-10-24 USB and hardening update](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792876959)** — LineageOS 24.0 / Android 17,
security patch **2026-10-01**. This update fixes USB File Transfer and duplicate
ADB interfaces, enables kernel page-table isolation, restores build/vendor checks
and corrects targeted SELinux labels. It retains the previous upstream LineageOS,
Wi-Fi tablet and UI/app improvements. Signed installation and recovery tests
preserved the original unlock pattern, setup and data.
Do not install images intended for the 2020 Exynos SM-P610/P615 or
LTE SM-P619.

Later builds appear under [Releases](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases).
The release includes the ROM, matching recovery/vbmeta package, SHA-256
checksums, and its exact source manifest. Google apps and app-root tools are
not included. Optional rooted ADB is a developer setting and is off on the
tested installation.

## Installing

1. Check **Settings → About tablet → Model**: this project targets SM-P613 only.
2. Back up your files. First installation requires an unlocked bootloader and
   a factory reset. The tested firmware base is `P613XXS7CXJ1`.
3. Download the release ROM and **matching recovery/vbmeta**
   assets, then verify them against that release’s `SHA256SUMS`.
4. Install the matching Lineage Recovery, format data, and sideload the ROM as
   described in [the installation guide](docs/installing.md).

Migration from danielml3’s ROM or another signing identity requires a clean
installation unless a separately tested migration procedure is provided.
Bootloader unlocking and a migration from stock firmware are not covered by
the tested procedure.

## Updating

OTA-enabled builds use **Settings → System → Updater**. Check for updates,
download the new build, and choose Install. This is a **non-A/B** device: the
installation reboots into recovery. Ordinary updates within this project’s
release-key channel should preserve apps and data; keep a backup.

The update feed is live and advertises the signed release.
Public Updater detection, download, signature verification, recovery installation
and reboot have passed without losing setup, the unlock pattern, or saved test
data. The test matrix records the details.
See [updating and recovery](docs/installing.md#updates) and [OTA maintenance](docs/ota.md).

## Bugs and development

Report the model, build date, steps to reproduce, and expected/actual behavior
in [Issues](https://github.com/tylxr59/lineageos-for-gta4xlveu/issues). Redact serial
numbers, network names/addresses, and personal information from logs. Problems
specific to this unofficial build belong here, rather than in official
LineageOS support channels.

- [Build from source](docs/building.md)
- [Maintaining and shipping updates](docs/maintenance.md)
- [Port findings](docs/port-findings.md)
- [Agent instructions](AGENTS.md)

Thanks to [LineageOS](https://lineageos.org/),
[Sevenrock](https://github.com/sevenrock),
[gta4xlve-dev](https://github.com/gta4xlve-dev), and
[danielml3](https://github.com/danielml3). This is an independent unofficial port.
