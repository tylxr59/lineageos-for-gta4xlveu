# LineageOS for Galaxy Tab S6 Lite (2022 Wi-Fi)

Unofficial **LineageOS 24.0 / Android 17** for the Samsung **SM-P613**, codename
**gta4xlveu**. Based on Sevenrock’s port and gta4xlve-dev / danielml3’s work.

**Status:** boots on an SM-P613. Encrypted data, SELinux enforcing, USB debugging,
and charging have been checked. Wi-Fi, front/rear cameras, speakers, and S Pen
writing/hover passed owner smoke tests. See [tested features](docs/testing.md)
for what remains unverified.

This repository holds installation guidance, reproducible source manifests,
and the update feed. The device, kernel, and vendor sources live in the
[linked forks](docs/building.md#sources).

## Downloads

There is **no public ROM release yet**. Private-key ROM/recovery installation
and a same-key update through Android Updater have passed on the test tablet,
including the original unlock pattern and data preservation. Do not install images intended
for the 2020 Exynos model, SM-P610/P615, or the LTE SM-P619.

Future builds will be listed under [Releases](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases).
Each release must include the ROM, matching recovery/vbmeta package, SHA-256
checksums, and its exact source manifest. Google apps and app-root tools are
not included. Optional rooted ADB is a developer setting and is off on the
tested installation.

## Installing

1. Check **Settings → About tablet → Model**: this project targets SM-P613 only.
2. Back up your files. First installation requires an unlocked bootloader and
   a factory reset. The tested firmware base is `P613XXS7CXJ1`.
3. Once a release is available, download its ROM and **matching recovery/vbmeta**
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

The update feed is live but currently empty, and Updater successfully checks it.
Signed local updates through Updater have been tested without losing setup,
the unlock pattern, or saved test data. Public ROM download and installation
through the feed await the first release.
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
