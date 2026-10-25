# Runtime fixes in development (2026-10-25)

Public release remains1792894491. The owner requested work on the runtime log
findings and was available for a no-wipe thermal-candidate installation. Signed
candidate1792933707 is now installed; no OTA publication/feed change occurred. See runtime-log-audit.md for the demonstrated failures.

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
Rooted debugging stayed off.

The clean full ROM/recovery build passed, including strict VINTF checks, and
candidate1792933707 was signed with the existing release identity. Whole-OTA,
120 standalone APK, 37 APEX container/payload and 26 nested APK signatures passed;
both OTA trust archives contain the single expected certificate. The embedded
vendor recovery and updater digest match the signed recovery. Boot/DTBO hashes
are identical to release1792894491. This is host compilation/signature evidence,
followed by the device checks recorded below. Standalone test
binaries accidentally included by an earlier target-files staging run were
quarantined; the rebuilt clean target files contain none. The exact resolved
candidate manifest is manifests/candidates/runtime-fixes-20261025.xml; its only
project revision change from the release is the shared Pixel HAL fork.

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
the legacy BTF validator supports kinds1–15. The inherited tree referenced a missing resolve_btfids host tool. An adapted
upstream v5.10 resolver initially stopped early when duplicate BTF type names
were counted twice; retaining the first matching ID fixes that lookup. The
udp6_sock type was present in the linked BTF, so this was not a missing-type
compiler problem. A further build failure exposed unconditional BTF references
to disabled fault-injection functions; those references now follow the matching
CONFIG_FAIL_PAGE_ALLOC/CONFIG_FAILSLAB guards. None of these changes bypasses
unresolved-ID validation. The first isolated Image build passed after these
repairs. The second build also passed using the committed native host-tool Makefile and
kernel dependency, replacing private diagnostic helpers. The duplicate-name
fixture reproduces the old resolver failure and passes with the corrected tool;
a missing-BTF negative fixture still fails as intended. Source is saved in the
kernel fork's wip/los24-dmabuf-iterator branch at423e21526 (host toolingbbac598e2,
conditional BTF IDs2756333ec). The feature remains default-off, with no release
manifest change. The resulting BTF contains173538 types, only supported kinds1–15, and the
DMA-BUF type ID resolves to5293. No successful boot, loader/CO-RE verification, live accounting, allocation-race
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


### Additional TI source-review findings

The saved prototype's stop routine unconditionally sets the feedback mux to
ZERO, including paths where it never acquired that mux. For example, a busy
PCM route causes start to return before changing any controls, then fallback
calls that stop routine. Production integration must track ownership and restore
the previous mux selection only when acquired; it must not reset another route.
This is a source-level cleanup defect, not a newly observed device failure.

The corresponding CAF external-hardware-plugin adapter already reference-counts
usecase categories before emitting first-enable/last-disable callbacks. A bitmask
inside the prototype is therefore not by itself proof of an overlapping-stream
bug; the closed installed HAL's callback behavior still needs verification.
No speculative refcount change or live audio override was applied.


## Thermal candidate local installation

Signed ROM1792933707 SHA256:
`14079a0541a608aea3618fca407e349bab1a875e9e7a6b74dec97239f488660d`.
No-wipe sideload and Android boot passed. The owner confirmed the usual pattern,
setup, Wi-Fi, both cameras, speakers, S Pen, auto-rotate and File Transfer.
The saved-file checksum and setup flags persisted. Live kernel config matches
the signed build; encryption remains file-based, SELinux enforcing, release keys,
UID2000 and Rooted debugging off. Crash buffer is empty.

Four repeated thermal dumps retain the four configured real CPU/GPU/battery
sensors and empty cooling list. The framework's headroom query returns expected
NaN because no skin model exists; no thermal API exceptions appeared during
boot or the query observation window. No threshold/status injection, hot test,
new cooling controller or fabricated sensor was used. The service binary's
SELinux label prevents ordinary-shell readback hashing, so no root was enabled
solely for that additional check.

Automatic recovery updating installed the matching recovery. Full boot, DTBO and
recovery partition hashes match signed target files, with original live vbmeta
unchanged. Boot/DTBO remain identical to public1792894491. Final recovery-menu
Android return passed with unlocked encrypted data and saved-file checksum
intact, thermal HAL ready, no observed thermal API exceptions, empty crash buffer
and Rooted debugging off. The owned marker and earlier native-test files were
removed; ordinary USB debugging remains on. The experimental DMA-BUF kernel and TI
work were excluded. No public OTA install/publication was repeated or claimed.
