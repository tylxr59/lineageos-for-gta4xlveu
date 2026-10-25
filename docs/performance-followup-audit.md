# ROM correctness and performance follow-up (2026-10-24)

Read-only review of public/installed build **1792876959**, device 02b4ef7,
kernel 0c5ccf4fc and vendor 1c0a6f2. No source tuning, device settings, root mode,
stress workload or release feed was changed. This is a source/runtime audit,
not a benchmark or a claim of measured performance improvement.

## 1. Android thermal feedback is absent: confirmed integration gap

`dumpsys thermalservice` reports `HAL Ready: false`, no cached temperatures and
no headroom thresholds. The framework log explicitly reports no Thermal HAL
service. There is no standard thermal HAL in the live service lists or device
manifest/packages. Adding the Pixel thermal Soong namespace does not install
its service or provide a device sensor configuration.

The vendor `thermal-engine` **is running** with its packaged configuration, and
70 thermal-zone types are readable, including CPU/SoC sensors. This is not proof
that hardware/vendor thermal protection is missing. The demonstrated gap is
between those mechanisms and Android's standard thermal status/notification API.
As described by [AOSP thermal guidance](https://source.android.com/docs/core/power/thermal-mitigation),
Android jobs and apps use that feedback to adapt under thermal stress. The
platform's ART configuration also sets a moderate-thermal-status dexopt cutoff.
Without usable framework feedback, that mechanism cannot be relied upon to
reflect actual device thermal conditions.

Next: map real sensor types/units and existing vendor throttling policy into a
standard thermal HAL, with appropriate VINTF and narrow access rules. Preserve
the vendor engine and factory limits. Do not invent cooler readings, relax trip
points or install a generic Pixel sensor configuration. Validate real readings,
severity callbacks and coexistence before claiming a working thermal interface.

## 2. App-launch bandwidth hint fails: confirmed performance lead

The running Pixel/libperfmgr Power HAL logged seven failed writes of `8137` to
`/sys/class/devfreq/soc:qcom,cpu-llcc-ddr-bw/min_freq`. Device powerhint.json
requests that value for the five-second LAUNCH boost. The hint is therefore not
being applied successfully in those observed transitions. Other hints may work;
this does not show the entire Power HAL is inactive.

The kernel's devfreq min_freq writer rejects a nonzero minimum greater than its
current maximum. The Atoll source OPP table includes 8137, so merely finding that
value in the table does not explain the live failure. A live cap, permissions or
another write error still needs to be distinguished. Normal ADB cannot inspect
all these nodes; failed shell access is not evidence that the HAL lacks access.
Its direct binder dump also fails from shell, which is not proof of a dead HAL.

Next: privileged read-only inspection of the active min/max/available values,
ownership/labels and write errno, then correct the hint or its access path.
Respect thermal caps. Compare launch timing and energy against the unchanged
release before promising a speed or battery benefit. CPU schedutil is active;
sampled cluster minima are 576 MHz/652.8 MHz, not permanently pinned at maximum.

## 3. BPF kernel-version override: confirmed compatibility exception

The product sets `ro.bpf.kver_override=5.10.239`; the actual kernel is 4.14.357.
Both the platform BPF loader and Connectivity's KernelUtils consume this
override. NetBpfLoad contains increasing kernel-floor checks, including 5.10
for 25Q4. This is a separate exception from the now-restored VINTF checks: passing
VINTF does not demonstrate every modern networking/BPF capability.

The maintained kernel has substantial BPF backports. Consequently the override
is not, by itself, proof that current networking is broken. Removing it blindly
would encounter version gates; reporting a newer release does not establish
that every selected helper/map/program feature is available either.

Next: enumerate selected BPF objects and required capabilities, inspect loader
results/pinned maps and exercise traffic accounting, firewall/VPN and relevant
network paths. Prefer explicit supported capabilities/backports over broad
version assumptions. Do not casually remove this property on the installed ROM.

The sample also contains 26 system-server errors opening the absent DMA-BUF BPF
iterator. libdmabufinfo tries that reader before a sysfs fallback; loading the
iterator is separately feature-flagged. Establish the fallback's accounting
coverage before treating this as a leak or merely suppressing the messages.
This error is not evidence that network BPF programs failed.

## 4. Graphics tuning deserves measurement, not speculative replacement

Several inherited SurfaceFlinger properties set early phase offsets to 100 µs;
the live dump confirms those offsets are active. Other old properties, including
debug.sf.hw and disable_backpressure, have no matching consumer in the inspected
SurfaceFlinger implementation. The latter should not be advertised as active
performance switches. Hardware composition is present; debug.sf.hw=0 does not
establish software-only rendering.

The small accumulated SystemUI/launcher frame samples contain jank and long
tails, but include startup/lock transitions and are not controlled comparisons.
Next: collect FrameTimeline/Perfetto during repeatable scrolling, launching and
video use, then compare current phase tuning with reviewed defaults. Do not
infer a frame-rate regression or a gain from those small historical samples.

## 5. ART and memory configuration cleanup: lower-risk maintenance candidate

Vendor properties still request `quicken`, duplicate dex2oat thread settings and
carry Samsung ro.slmk tuning. The inspected ART parser maps quicken to verify;
modern ART Service selects app compilation filters through pm.dexopt reasons.
Actual install/bg-dexopt properties are speed-profile, and dexopt records include
speed-profile and speed. The old properties do **not** prove apps are globally
uncompiled. See [ART Service configuration](https://source.android.com/docs/core/runtime/configure/art-service).

Next: remove demonstrably unused/obsolete properties in a separate small source
change and assess the remaining eight-thread compilation configuration under
launch/install load. Trace consumers before changing LMKD thresholds. Some
inherited pressure controls belong to an older strategy; do not assume changing
them improves Android 17's current kill decisions.

The normal-ADB snapshot shows roughly 1.66 GiB available out of 3.22 GiB visible RAM,
about 4 GiB configured swap with only a few MiB occupied, and an empty crash buffer.
Configured zram size is not an equivalent allocation of physical RAM. There were
26 cached-process kills clustered during boot/unlock; the later memory state
was normal. Neither snapshot proves steady-state app retention or battery life.
Increasing zram or disabling background apps indiscriminately is not justified.

## Limits and recommended order

Start with thermal integration and the failed launch hint. Audit BPF capability
coverage separately; profile graphics and memory before changing tuning. Keep
paused TI/Dolby work separate. Broad VTS/CTS, Bluetooth audio, microSD and
controlled battery/suspend endurance remain useful validation work.

The tablet was charging and recently rebooted during collection. Rooted debugging
remained off. Restricted GPU/zram/sysctl/HAL reads are unknowns, not failed
features. Broad shell service inspection itself generated SELinux find denials;
do not turn those into product-policy allow rules. Raw logs, app/process lists
and traces remain private. No new ROM build/install or OTA was performed.

## Improvement work in progress: no installation authorized

The owner subsequently requested improvements while explicitly prohibiting
flashing for now. Work branch `fix/los24-performance-followup` in the device fork
is separate from the release pins. Current source 72a336a is building; neither
compilation nor runtime success is claimed yet. Kernel/vendor remain unchanged.

A brief owner-authorized rooted-debugging inspection established the launch
hint's exact failure: the live LLCC-DDR maximum and highest advertised OPP are
**8136**, while the hint requested 8137. Other inspected bandwidth requests were
within their live limits. The source node/action now request 8136. The running
hint configuration was not changed. Rooted debugging was disabled afterward;
normal ADB reattached automatically and the self-deleting helper was absent.

The thermal candidate installs the existing Pixel AIDL HAL and its dedicated
executable label, starting it after boot. Hidden physical step-wise sensors are
unmonitored; only virtual one-to-one pass-through sensors are monitored. This
causes the upstream trip-initialization path to skip every physical sensor,
including if generic-netlink is enabled. No cooling devices or power hints are
configured. Reporting thresholds use observed CPU 120°C/GPU 95°C passive trips and
Samsung battery warm 42°C/overheat 50°C values. These are limited mappings of existing
policy, not a calibrated skin model or comprehensive thermal certification.
The source checker verifies this reporting-only contract and rejected five
unsafe mutations. Actual HAL startup/readings/callbacks and idle cost remain
unverified until a separately authorized test installation.

The cleanup removes obsolete quicken filters, the duplicate dex2oat thread entry
and two unused SurfaceFlinger switches. It preserves the current compilation
policy, active frame offsets and BPF override. A separate unapplied patch for a
platform-default frame-timing comparison is retained locally, not integrated
without a controlled comparison.

Privileged inspection found 146 pinned BPF objects and no BPF error lines in the
netd dump. This supports working current network integration, not complete API
coverage. The DMA-BUF iterator and `/sys/kernel/dmabuf/buffers` are both absent:
the fallback is unavailable too. This is a genuine telemetry gap, not merely a
missing iterator with a known-working fallback. An accurate solution needs a
reviewed kernel interface/backport; replacing unknown totals with incomplete
userspace counts or just hiding logs would not repair accounting. No such
kernel change is included in this candidate.

### Newer-kernel research lead

There is existing [SM7125 mainline work](https://github.com/sm7125-mainline/linux)
and a [Samsung A52/A72 tree](https://github.com/map220v/sm7125-mainline).
The inspected linux-6.14.7 branch includes Samsung A52/A72 and Xiaomi SM7125 device
trees, but no gta4xlve/P613 tree in the queried directory. This is a credible
separate research base, not evidence of Android/vendor compatibility on SM-P613.
A newer kernel could reduce future compatibility/backport burden, but does not
establish faster rendering or better battery life. Panel/S Pen, graphics/vendor
interfaces, cameras, audio, power and encryption/boot must be evaluated. No
kernel-port implementation, checkout switch or device experiment was started.


### Installation authorization and corrected build

The owner subsequently authorized a signed no-wipe test installation. Final
source d61cc85 adds the startup Power HAL client/config permissions and scheduled
IStats client access required by the inspected upstream implementation. The
corrected full build passed in3m46s; signing/runtime tests are still pending.
The earlier72a336a build also passed, but is superseded and must not be installed.
The [final candidate manifest](../manifests/candidates/performance-followup-20261024.xml)
keeps all1,242 paths and changes only the device project from the public release.
No new public OTA publication is authorized by this test request.


### Signed local candidate verification

Build1792893543 (device d61cc85) passed full target-files/recovery compilation,
strict VINTF, kernel/config and permissive-domain checks. Existing-key APK/APEX,
recovery trust, AVB and whole-file OTA signature verification passed. Boot and
DTBO remain byte-identical to release1792876959; the vendor recovery payload
and automatic updater target match the new signed recovery. Signed no-wipe
sideload transfer completed; Android/runtime validation is pending. No public
release or feed change has been made.

Source-matched compiled-policy queries confirm the thermal startup Power/IStats
Binder and scoped-property access. The inherited Qualcomm thermal domain already
has thermal sysfs write permission. This candidate adds read rules, but the full
policy does **not** prohibit writes. Its reporting-only behavior depends on the
reviewed configuration and upstream code paths (unmonitored physical sensors,
no trigger/severity references, no cooling devices), rather than an assumed
SELinux write barrier. An older host libsepol could not parse the Android policy;
queries were repeated using Android's matching libsepol instead.

The unlocked baseline trace yielded two cold Settings starts (718.45/694.13ms).
No attributable Settings FrameTimeline rows were available. This tiny sample,
with uncontrolled cache/thermal state, cannot establish general performance or
jank changes. An earlier locked-screen capture was excluded.


### Runtime rejection and ordering correction

Candidate1792893543 installed, but did not complete Android boot. Ordinary ADB
remained available. Android17's ThermalManagerService waits for declared IThermal
at PHASE_ACTIVITY_MANAGER_READY; scheduling that service on sys.boot_completed
created a startup cycle. This is a demonstrated integration defect, not a passed
hardware test. Do not reinstall or publish this candidate unchanged.

Device f38d06f moves the explicit service start to `on boot`, after post-fs-data
and before the framework wait. The corrected archive check now validates the
actual init action, rather than merely the presence of a start command. A full
replacement package is rebuilding; no wipe or vbmeta change is involved.


### Corrected signed Android test

Corrected build1792894491, device f38d06f, passed signed no-wipe installation and
Android boot. The owner confirmed the original pattern, setup, Wi-Fi, both
cameras, speakers, S Pen, auto-rotate and Dolphin File Transfer. The saved marker
checksum persisted; file encryption, enforcing SELinux, release keys, unchanged
kernel/config, normal ADB and Rooted debugging off passed. Crash buffer was empty.

Framework thermal feedback is now working: AIDL HAL ready, four CPU/GPU/battery
temperatures, threshold queries and registered listeners. Three samples over
12 seconds returned plausible readings; raw millidegree sysfs values confirmed
Celsius scaling. Captured boot logs contained no thermal-domain denials/fatal
errors. No induced-hot callback test, calibrated skin/headroom model or battery
endurance validation is claimed; headroom thresholds remain NaN.

Two candidate cold Settings launches measured693.94/699.44ms, similar to the
718.45/694.13ms baseline. This does not demonstrate a meaningful general speed
improvement. No new LLCC write errors appeared during the launch trace; source
requests the observed supported maximum8136. FrameTimeline attribution was absent.
Matching recovery boot and full boot/DTBO/recovery partition hashes passed;
the original vbmeta is unchanged. The final recovery-menu Android return and unlocked-data/security checks
also passed. The public release and OTA feed remain1792876959.


The thermal process used0.03 CPU seconds during a60.08-second observation
(0.05% of one CPU), without restarting. This short, charging observation during
owner checks is not an idle power/battery endurance result. BPF capability
coverage, DMA-BUF accounting interfaces and controlled graphics comparisons
remain separate unresolved work; no speculative kernel/backpressure change was
included in this tested candidate.


Final return repeated HAL-ready/four-reading checks and retained the saved marker
checksum, enforcing SELinux, encrypted unlocked data, normal ADB, disabled Rooted
debugging and an empty crash buffer. The owned marker and Perfetto configuration
were removed; both owned on-device trace paths are absent. No persistent logger,
app-root or new public release was added. This is a tested local candidate;
public release/feed1792876959 remains unchanged.


## Published release1792894491

The owner subsequently requested publication. [The public release](https://github.com/tylxr59/lineageos-for-gta4xlveu/releases/tag/lineage-24.0-20261024-gta4xlveu-1792894491) is the
exact tested signed1792894491 bundle described above, not the rejected
1792893543 image. All12 asset sizes and GitHub SHA256 digests, downloaded ROM and
checksums, and the canonical five-entry HTTPS feed on host/tablet matched.
Resolved/fork manifests pin the tested source. The tablet already ran this build;
no additional older-to-newer public Updater installation is claimed. Previous
references to unchanged public pins/feed describe the earlier local-test stage.
