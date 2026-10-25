# Building

## Sources

| Component | Repository | Maintained revision/branch |
| --- | --- | --- |
| Platform | [LineageOS/android](https://github.com/LineageOS/android) | LOS24; exact project pins in manifests |
| Device | [device fork](https://github.com/tylxr59/android_device_samsung_gta4xlveu) | fix/los24-performance-followup |
| Kernel | [kernel fork](https://github.com/tylxr59/android_kernel_samsung_gta4xlve) | fix/los24-hardening |
| Vendor | [vendor fork](https://github.com/tylxr59/android_vendor_samsung_gta4xlveu) | fix/los24-hardening |

`manifests/known-good.xml` records the tested prototype. `manifests/resolved.xml`
pins the release-key source including the OTA endpoint, Gatekeeper
policy fix, Wi-Fi-only tablet configuration and lock-icon overlay. The local manifest
`manifests/gta4xlveu.xml` supplies the maintained device forks when following the
upstream platform branch. Do not replace the fixed kernel/device pins with the
unmodified imported branches.

## Environment

Use Linux x86_64 and the [LineageOS build guidance](https://wiki.lineageos.org/devices/).
The tested environment is Ubuntu 24.04, 24 logical CPUs, 62 GiB RAM plus swap,
and several hundred GiB of free storage. Allow at least 500 GiB of usable space
for source/builds and extra room for archived target files and releases. Check
actual space, RAM/swap, filesystem, OS, and tool availability before syncing.

An optional workspace-local rootless Ubuntu wrapper is included. It needs
unprivileged user/mount namespaces, subordinate UID/GID mappings, curl, tar and
unshare on the host. `tools/setup-ubuntu` installs packages **inside Ubuntu**,
not on the host. The wrapper binds the workspace, /proc, /dev and /sys; it is a
build convenience, not an isolation boundary. Inspect the host OS before
installing prerequisites; do not assume the host is Ubuntu.

For a new standalone workspace:

```sh
git clone https://github.com/tylxr59/lineageos-for-gta4xlveu
cd lineageos-for-gta4xlveu
tools/setup-ubuntu
tools/ubuntu-run git config --global user.name YOUR_NAME
tools/ubuntu-run git config --global user.email YOUR_EMAIL
tools/ubuntu-run git lfs install --skip-repo
tools/ubuntu-run tools/sync-source pinned
tools/ubuntu-run tools/build
```

The `repo` launcher and Git LFS are required. Shallow/no-tag syncing reduces
history downloads; deepen individual repositories when debugging requires it.
The pinned manifest is served from this repository; `github` remotes use an
absolute fetch URL so it is portable between manifest repositories.

For an existing checkout, preserve worktrees and inspect dirty repositories
before running sync. `LOS24_WORKSPACE` can point `tools/build` and
`tools/sync-source` to an existing directory containing android/. Invoke these
inside its configured Ubuntu environment. Do not run this public checkout’s
Ubuntu setup over an existing environment just to reuse the source checkout.

Direct build inside a configured environment:

```sh
cd android
source build/envsetup.sh
breakfast gta4xlveu userdebug
m -j4 bacon recoveryimage
repo manifest -r -o ../artifacts/prebuild-manifest.xml
```

`tools/build` records the manifest **before** compilation. Choose jobs to fit
RAM/swap. Initial full compilation is much slower than small incremental builds;
recent incremental image/package rebuilds took about 5–8 minutes. Use a temporary
sleep inhibitor and a durable log/status runner for long builds; do not change
persistent host power settings.

The build helper defaults to four jobs; set `LOS24_JOBS` explicitly when more
memory is available. Size concurrency against **available** RAM on a shared
host, not installed RAM alone. The Wi-Fi-tablet product reconfiguration caused
broad SDK/app rebuilds and exhausted memory at higher concurrency. Cached
configuration and completed compilation work can be reused after an interrupted
build. Monitor memory/swap and the host's memory-pressure manager.

Go runtime budgets also require care: Soong's generated bootstrap command uses
`env -i`, and the main executor filters its environment. Simply exporting
`GOMEMLIMIT` does not prove that either process received it. The successful retry
used a 24 GiB/eight-CPU generator budget, a 12 GiB Siso budget, and four compile
jobs. Verify the effective process environment; keep any launcher adaptation
separate from Android source changes, and refresh generated bootstrap rules
when upstream build-tool sources change.

## Output and release signing

Outputs are under `android/out/target/product/gta4xlveu/`. `bacon` produces the
full non-A/B OTA; `recoveryimage` produces recovery. The device tree also creates
a recovery/vbmeta tar. Keep exact source manifest, target-files archive, OTA,
matching image set, checksums, build log and signing certificate for each build.
Do not assume loose output images are byte-identical to OTA images: compare the
actual OTA/target-files images and use those for installed-image checks.

Default `bacon` output is development/test signed. A public release needs the
separate persistent-private-key signing step in [OTA maintenance](ota.md).
Check ZIP integrity, OTA certificate and whole-file signature, AVB image set,
VINTF results, actual ramdisk/system/vendor contents, and hardware boot. Retain
the historical kernel-requirements bypass in the risk record. The current
release restores checks with genuine toolchain detection and enforcing CFI; see
[the VINTF audit](vintf-audit.md). Never replace kernel inputs with diagnostic
configuration claims.
