# Runtime fixes in development (2026-10-25)

Released/installed baseline remains1792894491. The owner requested work on the
runtime log findings. No replacement ROM installation or OTA publication has
occurred. See runtime-log-audit.md for the demonstrated failures.

## Thermal API fix

The shared Pixel thermal AIDL implementation now returns a successful empty
list when configuration has no visible matching sensor/device. It checks
initialization first, and still propagates failures when a matching configured
sensor/cooling device cannot be read. This covers absent TYPE_SKIN readings and
thresholds, hidden sensors, and the deliberately empty cooling-device list.
No fabricated SKIN sensor, cooling control or temperature was introduced.

Source is maintained in [the Pixel hardware fork](https://github.com/tylxr59/android_hardware_google_pixel),
branch fix/los24-thermal-empty-queries, commitd4f83b6. Base8bd3c71 is the exact
released LineageOS project revision; no unrelated platform update was included.
This is a fourth source fork for a shared HAL defect; the three existing
Samsung device/kernel/vendor forks are retained. Candidate fork overrides live
in manifests/candidates/runtime-fixes-forks-20261025.xml; release pins/feed remain
unchanged until a separately authorized and validated release.

The service and arm32/arm64 test binaries compiled. All11 native tests passed on
the owner's tablet under ordinary ADB UID2000: ten API regression cases plus the
existing asynchronous-callback test. These are tests of the patched AIDL class
with a mock helper, not a replacement of the installed HAL or a boot test.
The upstream test module incorrectly included service.cpp, whose main entered
the service daemon instead of gtest_main; the test module now excludes that
entry point and requires no root. Vendor HAL library labels prevent ordinary
shell linkage, so the standalone test used temporary local copies of five
matching signed-release shared libraries. Binary and library copies were removed;
Rooted debugging stayed off. Full ROM/recovery/VINTF build is in progress.

## DMA-BUF: isolated BPF iterator experiment

The existing4.14 kernel already contains backported BPF iterator machinery,
but has no DMA-BUF target and CONFIG_DEBUG_INFO_BTF is disabled. The modern
Android object uses CO-RE field reads and the iter/dmabuf target. A version
property cannot supply that missing target/type metadata.

An isolated kernel worktree adapts the seq-file iterator from
[Linux v6.18 kernel/bpf/dmabuf_iter.c](https://github.com/torvalds/linux/blob/v6.18/kernel/bpf/dmabuf_iter.c).
It adds an opt-in DMABUF_BPF_ITER option and reference-safe global-list traversal.
The legacy implementation acquires the next file reference while holding the
list mutex, then releases the previous reference after unlocking. This avoids
relying on modern deferred-file-release behavior while porting to older lifetime
rules. Existing debug reference tracking is balanced. It adds no per-allocation
sysfs objects or extra buffer allocation/free hooks.

The experiment enables BTF and that option only in its separate output config.
The pinned pahole1.25 invocation skips enum64/decl-tag/type-tag encodings because
the legacy BTF validator supports kinds1–15. The kernel is building separately;
no successful boot, loader/CO-RE verification, live accounting, allocation-race
stress, suspend or performance result is claimed. The existing kernel and ROM
build outputs remain separate. The userspace BPF-version override is unchanged;
this experiment would not certify all claimed modern kernel capabilities.

Do not replace the missing statistics with partial process totals, expose
writable debugfs, loosen SELinux or simply suppress the errors. This experiment
is not an installable or release-ready fix yet.

## TI audio: confirmed route-level prerequisite

Current device configuration still selects ACDB14 for speaker/reverse speaker.
The earlier ACDB inspection mapped that to topology0x112fc, while the successful
TI receive path required ACDB15/topology0x1000fc01 plus input102/0x1000fd01 and
QUIN feedback TX→RX registration. Kernel unmute currently attempts the TI IV/VBAT
configuration regardless of whether that TI receive topology is in the route.
The observed module0x1000fc00 parameter rejections match this known mismatch.

The saved integration remains separate from the thermal/DMA-BUF candidates.
Correct resolution needs the complete playback/feedback lifecycle, busy capture
and output-switching/failure handling; skipping the error or enabling profile15
alone is not a fix. Calibration/gain/protection and the working profile14 fallback
stay untouched. No live audio experiment was performed during this work.
