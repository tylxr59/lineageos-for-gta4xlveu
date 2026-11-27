# Battery and standby investigation

Initial read-only investigation on2026-10-24 used the unchanged public
release1792787032, normal ADB and enforcing SELinux. No battery statistics were
reset, settings spoofed, governors changed or power services disabled.

## First overnight result

The owner reported roughly100% to70% after about30 minutes of video and10 hours
with the screen off. Android recorded28–29 percentage points discharged across
its approximately13-hour battery interval, with24 points during screen-off.
That interval was not a clean standby test: a dashboard app with live camera
cards had hours of background video, substantial network transfer and long
app-held partial wake locks. The video player also accumulated hours of
screen-off audio despite the owner intending to close it. Raw app attribution,
network data and logs remain private; these are not generic device defaults.

The CPU was awake for roughly9h36 of12h55 on battery, while Android reported
about11h40 in deep Doze. Doze state alone therefore did not demonstrate hardware
suspend. The final approximately3h25 had no reported percentage change after
background media activity ended. This is coarse gauge evidence, not proof of
zero consumption, but it argues against assuming an always-awake kernel defect.
At the later inspection, no codec resources were allocated and the remaining
video-player track was paused.

No hardware battery-life or deep-suspend pass is claimed. The evidence points
first to background app/media activity; a controlled overnight baseline remains
pending. Do not introduce app-specific ROM blacklists or speculative governor,
Wi-Fi, Bluetooth, SELinux or service changes to conceal this workload.

## Controlled follow-up

1. Preserve the initial logs. Before the next interval, record percentage, time,
   charging state and a fresh read-only battery snapshot. Do not reset stats.
2. For one comparison night, force-stop the dashboard and video apps. Closing a
   window or swiping Recents does not establish that playback and services ended.
   Force-stopping also stops that app's background functions until it is reopened.
   Leave ordinary Wi-Fi/settings consistent and disable any keep-awake utility.
3. Physically unplug and turn the screen off. Avoid continuous ADB polling,
   logging apps, forced Doze or framework-only battery-unplug simulation.
4. In the morning, record percentage/time before charging materially changes
   the level, then reconnect for another snapshot. Compare discharge per hour,
   screen-off elapsed time versus uptime, wake locks, media and network activity.
   Check for a statistics rollover before comparing cumulative counters.
5. If the quiet baseline improves, reintroduce one app/workload at a time. If it
   remains poor without app activity, investigate kernel wake sources and power
   HAL behavior with targeted diagnostics. Keep root debugging off afterward.

Use percentage/time and suspend evidence as the primary comparisons. The
fuel-gauge charge-counter implementation derives a value from configured
capacity and raw SOC; software power estimates are not laboratory measurements
of physical capacity, battery health or individual component consumption.


## Owner follow-up report (2026-10-25)

On release1792894491, the owner reports starting at100%, playing YouTube for
about30 minutes, force-stopping YouTube, and waking to97%. Exact overnight hours
and start/end diagnostics were not supplied. This is3 percentage points combined
playback/standby, substantially better than the earlier confounded100→70 report.
It supports background workload as the earlier cause, but does not isolate
standby energy, prove deep suspend or establish a measured ROM power improvement.
No power/governor tuning was made in response.


## Low-battery shutdown behavior (issue #7, 2026-11-27)

A user reported shutdowns shortly after the indicator showed 2–3%, with the
charger then reporting 0%. Source review of release1793916221 (kernel
`be84fa84d`, no device test of a full discharge):

- `BatteryService.shouldShutdownLocked()` shuts down only when the reported
  level is 0 and not charging. The health HAL reports capacity level
  unsupported (-1), so no separate critical-level trigger applies.
- The SM5714 fuel-gauge driver and `atoll-sec-gta4xlve-battery-common.dtsi`
  values are Samsung's, unchanged by our forks. Atomic capacity reporting moves
  at most 1% per poll (30s discharging poll interval). Below the 3.2V SW
  voltage-empty alarm (`sw_v_empty_voltage`, recovery 3.48V), the driver
  decrements SOC by 1% per update until 0. Below 10°C it switches to HW
  voltage-empty mode at ≤5% raw.
- A heavy load near empty therefore produces a quick 3→0 walk and a normal
  Android shutdown. Aged or cold cells sag sooner.

`persist.sys.boot.reason.history` is readable by normal ADB (UID2000) and
distinguishes `shutdown,battery` from a sudden power loss. Do not lower the
voltage-empty thresholds or fake SOC to extend runtime: they protect against
deep discharge. The reported charge counter derives from
`fuelgauge,capacity = 5000` rather than the 7040mAh cell; that is cosmetic and
unrelated to the shutdown point.
