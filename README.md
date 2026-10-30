<h1 align="center">LineageOS for Galaxy Tab S6 Lite (2022 Wi-Fi)</h1>

<p align="center">
  Unofficial <strong>LineageOS 24.0 / Android 17</strong> for the Samsung <strong>SM-P613</strong> (<code>gta4xlveu</code>).
</p>

<p align="center">
  <a href="https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/tylxr59/lineageos-for-gta4xlveu?display_name=tag&sort=date"></a>
  <img alt="Android 17" src="https://img.shields.io/badge/Android-17-3ddc84">
  <img alt="Security patch 2026-10-01" src="https://img.shields.io/badge/security%20patch-2026--10--01-blue">
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-97ca00"></a>
</p>

<p align="center">
  <a href="#-features">Features</a> ·
  <a href="#-installing">Installing</a> ·
  <a href="#-updating">Updating</a> ·
  <a href="#-troubleshooting">Troubleshooting</a> ·
  <a href="#-development">Development</a>
</p>

---

Based on Sevenrock’s port and gta4xlve-dev / danielml3’s work. This repository
holds installation guidance, reproducible source manifests, and the update feed.
The maintained ROM sources live in the [linked forks](docs/building.md#sources).
See [CHANGES.md](CHANGES.md) for release changes and their source commits.

> [!WARNING]
> SM-P613 only. Do not install these images on the 2020 Exynos SM-P610/P615 or
> the LTE SM-P619.

> [!NOTE]
> Google apps and app-root tools are not included. Optional rooted ADB is a
> developer setting and is off on the tested installation. This is an
> independent unofficial port.

## 🎯 Features

| Feature | Status |
| --- | --- |
| 🔐 **Encrypted data, SELinux enforcing** | Checked on every release. |
| 📶 **Wi-Fi, cameras, speakers, S Pen** | Front/rear cameras, speakers, S Pen writing/hover pass owner smoke tests. |
| 🎧 **Bluetooth audio** | AirPods Pro 2 AAC media playback, disconnect fallback and reconnect. |
| 🔌 **USB** | Debugging, file transfer (MTP) and charging. |
| 🛰️ **Assisted GPS switch** | Starts and stops Qualcomm's background satellite-assistance downloads; ordinary GPS works with it off. |
| 🔄 **OTA updates** | Signed releases through **Settings → System → Updater**. |

See [tested features](docs/testing.md) for what remains unverified.

## 📥 Downloads

**[Download the Assisted GPS update](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261029-gta4xlveu-1793279242)**,
build **1793279242**. Signed no-wipe installation, data/setup persistence, owner
hardware checks and matching recovery passed. Prior OOM, accounting, hardening,
Bluetooth audio and tablet fixes remain.

Each release includes the ROM, matching recovery/vbmeta package, SHA-256
checksums, and its exact source manifest. Later builds appear under
[Releases](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases).

## 📋 Requirements

- A Samsung Galaxy Tab S6 Lite 2022 Wi-Fi, **SM-P613** (check **Settings → About tablet → Model**).
- An unlocked bootloader. Unlocking trips Knox and is not covered by the tested procedure.
- Firmware base: the maintainer tested `P613XXS7CXJ1`; a
  [community report](https://github.com/tylxr59/lineageos-for-gta4xlveu/issues/2)
  also confirms `P613XXS8CYE1` (bootloader binary 8) without downgrading.
- Heimdall or Odin, and `adb` on your computer.

## 🚀 Installing

First installation requires a factory reset, so back up your files first.

1. Download the release ROM and **matching recovery/vbmeta** assets, then verify
   them against that release’s `SHA256SUMS`.
2. Flash the matching Lineage Recovery and vbmeta from Download Mode.
3. Boot recovery, format data, and sideload the ROM:

   ```sh
   adb sideload lineage-24.0-YYYYMMDD-UNOFFICIAL-gta4xlveu.zip
   ```

The [installation guide](docs/installing.md) has the full steps.
MindTheGapps has a [community report](docs/installing.md#optional-google-apps)
but is not maintainer-tested.

Migration from danielml3’s ROM or another signing identity requires a clean
installation unless a separately tested migration procedure is provided.

## 🔄 Updating

OTA-enabled builds use **Settings → System → Updater**. Check for updates,
download the new build, and choose Install. This is a **non-A/B** device: the
installation reboots into recovery. Ordinary updates within this project’s
release-key channel should preserve apps and data; keep a backup.

Public Updater detection, download, signature verification, recovery installation
and reboot have passed without losing setup, the unlock pattern, or saved test
data. See [updating and recovery](docs/installing.md#updates) and
[OTA maintenance](docs/ota.md).

## 🩺 Troubleshooting

| Symptom | Fix |
| --- | --- |
| Signature error while sideloading | Stop. Check that the ROM, recovery and published certificate come from the same release. |
| ADB progress stops around 47% | Normal. Rely on recovery's **Install complete** message. |
| Android doesn't start | Return to recovery and collect a redacted recovery log before changing more partitions. Don't repeatedly wipe data. |
| Heimdall connection failures | Use a fresh blue Downloading screen for each session; see the [installation guide](docs/installing.md). |

## 👋 Development

- [Build from source](docs/building.md)
- [Maintaining and shipping updates](docs/maintenance.md)
- [Port findings](docs/port-findings.md)
- [Agent instructions](AGENTS.md)

Report the model, build date, steps to reproduce, and expected/actual behavior
in [Issues](https://github.com/tylxr59/lineageos-for-gta4xlveu/issues). Redact serial
numbers, network names/addresses, and personal information from logs. Problems
specific to this unofficial build belong here, rather than in official
LineageOS support channels.

## 🤝 Acknowledgements

Thanks to [LineageOS](https://lineageos.org/),
[Sevenrock](https://github.com/sevenrock),
[gta4xlve-dev](https://github.com/gta4xlve-dev), and
[danielml3](https://github.com/danielml3). Thanks also to
[Nokuty](https://github.com/Nokuty) for the first community install report on
bootloader binary 8 with MindTheGapps ([#2](https://github.com/tylxr59/lineageos-for-gta4xlveu/issues/2)).

## 📃 License

This repository's documentation and tools are available under the [MIT License](LICENSE).
The ROM itself is built from LineageOS and Android sources under their own licenses.
