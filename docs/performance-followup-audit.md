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
