# Runtime log audit: release1792894491

Read-only collection on 2026-10-24, approximately15 minutes into the current
Android boot. Normal ADB UID2000; no root, settings changes, stress workload,
reboot, installation or log-buffer clearing. Raw logs remain private. This is a
snapshot, not long-term stability or comprehensive kernel certification.

## Current stability

The crash buffer was empty. Captured logs contained no Java/native fatal crash,
ANR, watchdog kill or SELinux denial. ActivityManager reported no ANR since boot.
A filesystem keyword match was `fsck.f2fs: Info: No error was reported`, not a
filesystem failure. Historical DropBox watchdog records at22:13–22:24 belong to
the rejected1792893543 thermal-startup-cycle test, before this boot at22:31;
do not present those as new failures of1792894491.

## Actionable follow-ups

### Thermal API treats an unsupported sensor type as a read failure

Four observed exception stacks were for IThermal.getTemperatureThresholdsWithType,
called by the framework's TemperatureWatcher for TYPE_SKIN, at boot and during
our thermal dumps. No skin sensor/model is configured. Pixel thermal helper
fillTemperatureThresholds returns false for an empty filtered result, which its
Binder wrapper converts into EX_ILLEGAL_STATE with a generic sensor-read error.

CPU/GPU/battery queries still return all four real readings; the HAL remains
ready. This is an API edge-case defect, separate from a sensor failure. Review
handling of legitimate empty typed results, distinguishing them from real read
and initialization failures. The interface documents initialization failure as
EX_ILLEGAL_STATE. Review similarly empty temperature/cooling queries and add
focused coverage before building. Do not fabricate a SKIN sensor or cooling
device to suppress the exception. No fix or new build was made during this audit.

### TI SmartPA configuration rejection persists

Audio DSP logs include ADSP_EBADPARAM for AFE_PORT_CMD_SET_PARAM_V3 (0x100fa).
Adjacent kernel lines identify TI SmartPA module0x1000fc00 and failures configuring
IV format / TAS_SA_IV_WIDTH_VBAT_MON. These occurred beyond boot, including the
latest captured playback route transition. The same named IV-configuration
failures exist in the earlier TI investigation logs; this is not established as
a regression from the thermal update.

Speaker playback passed owner testing, but that does not establish correct TI
feedback/processing. This is a concrete lead for the paused audio work. Preserve
factory calibration and protection; do not change gain, force profile15 alone,
or resume the unvalidated audio candidate as a generic log cleanup.

### DMA-BUF accounting gap remains

The loader cannot load dmabufIter.bpf. System-server logs repeatedly show both
the absent pinned iterator and absent /sys/kernel/dmabuf/buffers fallback (17
instances of each in this capture). This is missing accounting support, not
proof of a memory leak or network-BPF failure. See the performance audit for
capability/backport review requirements; do not substitute incomplete totals.

## Lower-priority vendor findings

- Camera EEPROM/I2C timeouts (rc-110) and VFE initialization errors were clustered
  during boot. Both cameras passed owner use. Sensor probing/calibration paths
  merit targeted review, but no continuing capture failure was demonstrated.
- Samsung USB thermal code repeatedly reports an invalid temperature-check type.
  Source sec_usb_thm_overheatlimit explicitly substitutes battery temperature when
  usb_temp_check_type is NONE. The same message predates this release. It does
  not by itself prove overheating; independent connector-temperature coverage
  requires separate hardware/configuration review.
- Display logs report a missing candela map table, also present in the prior
  audit. Review brightness mapping if behavior is abnormal; the error priority
  alone does not establish a rendering fault.

Prioritize correct thermal empty-query behavior, then the documented TI path and
DMA-BUF capability work. No evidence in this snapshot establishes an urgent
crash/data-loss regression or requires abandoning the planned battery baseline.
