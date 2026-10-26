# BPF and legacy vendor compatibility review

Reviewed on 2026-10-26 against released and installed **1793018822**. This is a
source, immutable target-files and read-only device audit. Temporary Rooted
debugging and a removed read-only query helper were used for runtime inspection.
No ROM source, image or OTA feed was changed, and no ROM was built or flashed.
Earlier codec, FUSE load-gating, atomic and hardening defects are already fixed
in this release; see [the preceding audit](security-compatibility-audit.md).

## Findings and priorities

| Priority | Finding | Next step |
| --- | --- | --- |
| 1 | The kernel's live OOM tracepoint has only a PID, while the shipped BPF reader expects a richer record. | Review/backport the upstream tracepoint extension, then validate the actual layout and memory-event path. |
| 2 | Kernel-version selection combines the device override with compile-time minimum assumptions. Removing the property alone cannot make all feature checks truthful. | Inventory and test each required capability before changing selection. Preserve networking and accounting. |
| 3 | Legacy crypto consumers use a different ASN.1 structure ABI from the current platform library. | Preserve the existing library; establish an ABI-preserving source/patch baseline before proposing replacement. |
| 4 | Protobuf 3.9.1 has camera, sensor and DRM consumers. Some direct dependencies have no direct symbol imports. | Review dependency closures and actual dynamic loading before pruning or replacing anything. |

These findings do not establish an exploited vulnerability, a user-visible OOM
failure, or an observed camera/credential regression. Loading a BPF program and
resolving ELF symbols do not establish data-layout or behavioral compatibility.

## BPF: what the override actually does

The real kernel is `4.14.357`; device `properties/product.prop` sets
`ro.bpf.kver_override=5.10.239`. Two source entry points consume it:

- Connectivity `bpf/headers/include/bpf/KernelUtils.h` caches an effective
  version. Its shared helpers reach networking, statistics and memory events.
- `system/bpf/loader/bpfloader.rs` independently parses it to select map/program
  minimum/maximum version ranges.

There is another layer: **non-APEX API-37 builds compile in a minimum kernel of
5.10**. `isAtLeastKernelVersion()` returns true for thresholds at or below that
minimum even when `kernelVersion()` reports an older kernel. APEX builds use a
minimum of zero and compare the reported version. A host probe compiled the
actual unchanged header with controlled `uname` and property input:

| Build context | Property | Reported version | At least 5.10 |
| --- | --- | --- | --- |
| Platform, API 37 | Absent | 4.14.357 | Yes, compile-time assumption |
| Platform, API 37 | 5.10.239 | 5.10.239 | Yes |
| APEX, API 37 | Absent | 4.14.357 | No |
| APEX, API 37 | 5.10.239 | 5.10.239 | Yes |

This is a controlled host source test, not four different device installations.
It explains why simply deleting the property is not a complete cleanup.

### Selected paths and existing backports

| Selected behavior | Relevant source | Evidence / boundary |
| --- | --- | --- |
| Networking minimum-version admission | `Connectivity/bpf/loader/NetBpfLoad.cpp`, `bpf/netd/BpfHandler.cpp` | Lowering the effective version can reject startup before feature-specific fallbacks. |
| Bulk map lookup/delete and statistics | `bpf/headers/include/bpf/BpfMap.h`, `BpfNetworkStats.cpp` | Kernel `syscall.c` and map implementations contain batch APIs. Source presence is not exhaustive runtime proof. |
| Mappable arrays and BTF handling | `NetBpfLoad.cpp` | Kernel has real map mmap/BTF backports; effective version changes flags and BTF sanitization. |
| Socket storage, release, bind/connect, UDP and sockopt hooks | `BpfHandler.cpp`, `bpf/progs/netd.c` | Real kernel hook implementations exist. Startup attach/query checks exercise several paths, but do not certify all socket semantics. |
| Ring buffers and memory-event readers | `system/memory/libmeminfo/libmemevents/` | Ring buffers are backported, but the OOM event layout below is incompatible. |
| Tethering program variants and helpers | `Connectivity/bpf/progs/offload.c` | Version ranges choose different compiled programs. Review actual helper and packet behavior before changing ranges. |
| Atomic wakelock accounting and DMA-BUF iteration | Kernel backports and platform BPF objects | Passed the previous bounded live tests; preserve those regressions during future selection changes. |
| FUSE-BPF backend | `system/bpf/loader/bpfloader.rs` | Already capability-gated by the actual kernel entry. Ordinary FUSE fallback remains intentional. |

The kernel is substantially backported; it is not an untouched 4.14 kernel.
Conversely, the override does not establish full 5.10 capability coverage.

**Future update tripwire:** the pinned Connectivity loader requires 5.15 when
the platform full API reaches **37.1** (`isAtLeast26Q4`, `api_level_full>=3710`).
The current device reports **37.0**. Review this before a platform sync changes
the full API level; do not respond by raising the override to another untested
version. This is a source condition, not a prediction of upstream release timing.

### Concrete OOM tracepoint incompatibility

The tablet permits ordinary shell to read
`/sys/kernel/tracing/events/oom/mark_victim/format`. Its only event-specific
field is `int pid`, at offset 8, size 4. The kernel source agrees:
`include/trace/events/oom.h` and `mm/oom_kill.c` use the old PID-only event.

The shipped `SYSTEM/etc/bpf/memevents/bpfMemEvents.bpf` was extracted from signed
target files and disassembled. Its AMS OOM program reads the PID at offset 8,
then expects command-name location at 12, memory counters from 16, UID at 48,
page-table usage at 56 and `oom_score_adj` at 64. The actual source header
`libmemevents/include/memevents/bpf_types.h` has a 72-byte fixed structure on
LP64. Those additional fields are absent from the live tracepoint.

Thus a successfully loaded program is insufficient: the OOM reader's data ABI
does not match its producer. The audit did not trigger an OOM, induce memory
pressure, or demonstrate what records a live OOM would deliver. Follow-up
inspection found the AMS OOM program loaded and pinned but no active OOM perf
attachment in that snapshot. This is a latent producer/reader compatibility
defect, not evidence of currently delivered corrupt OOM records. Four LMKD
reclaim/kswapd programs were attached. Why the AMS listener was not attached was
not established from the available logs.
The corresponding vmscan wake/sleep format was also captured for comparison;
their fixed fields agree with the reader's expected offsets.

There is an existing upstream repair: **mm: update mark_victim tracepoints
fields**, available as Android common commits
[`3507c287`](https://android.googlesource.com/kernel/common/+/3507c287a681cab08d81e41df9618d36ed572118)
and the older-kernel backport
[`338203a8`](https://android.googlesource.com/kernel/common/+/338203a817216e1cd81b7a19f734f58cf59ff658).
The latter changes the tracepoint and its call site, collecting the required
task, credential and memory information. The reviewed patch has not been
applied. Adapt it against the actual 4.14 task/mm locking and credential lifetime
rules rather than copying a newer implementation blindly.

For validation, compare all emitted fields/offsets against the real BPF object,
compile the affected kernel/tracepoint users, then test bounded synthetic event
decoding and normal memory-event operation. Any deliberate OOM/end-to-end kill
test needs separate consideration; do not run a global OOM/sysrq test on the
owner's active tablet as a routine check.

### Approach to capability cleanup

First fix demonstrated ABI mismatches such as the OOM event. Then build a
capability matrix covering batch maps, mmap, ring buffers, socket storage,
attach/query hooks, helpers and program variants. Treat permission failures as
permission failures, not absent features. Probe on temporary isolated objects;
never delete or repurpose Android's live pinned maps/programs. Preserve useful
hard errors instead of silently disabling essential networking.

Only after those results should the loader/header policy distinguish actual
kernel identity, supported backports and platform admission. That involves both
Connectivity and the Rust loader, and potentially platform consumers compiled
with minimum-version assumptions. A broad new fork is not justified merely to
rename the override. Keep it until a tested replacement exists.

## Legacy libraries: shipped consumers and provenance

The audit inspected dynamic dependencies/exports/imports of **3,025 ARM ELF
files** from signed target files across system/vendor/product/system_ext/ODM.
APEX payloads and non-ARM firmware are outside this scan. Direct dependency
counts include both ABIs where installed. They do not measure runtime use or
cover `dlopen`/symbol lookup strings and transitive dependencies.

| Library | Direct consumers | Role and action |
| --- | --- | --- |
| `libcrypto-v33.so` | 3, all 64-bit | Samsung Gatekeeper, keymaster helper and keymaster implementation. Preserve credential/key continuity. |
| `libcrypto_shim.so` | 2, both 32-bit | Widevine libraries import `CBS_init`; the source provides three small CBS accessors, not an old full crypto engine. |
| `libui_shim.so` | 4, scaler libraries in both ABIs | Actual imports need old `GraphicBufferMapper::lock` and synchronous `unlock` signatures. Preserve camera/scaler behavior and fence waiting. |
| `libprotobuf-cpp-full-3.9.1.so` | 12 | Camera/NN dependencies and an inherited radio blob; several have no directly matched protobuf imports. |
| `libprotobuf-cpp-lite-3.9.1.so` | 10 | Sensors and Widevine. Genuine imported parser/runtime symbols exist. |

The inherited radio blob is not evidence of cellular functionality on SM-P613.
Do not strip shared vendor dependencies just because this is a Wi-Fi product.
Zero direct symbol matches also do not establish safe removal: transitive and
runtime loading paths must be checked first.

### Crypto: known origin, genuine ABI obstacle

Lineage's introduction commit
[`353e696c`](https://github.com/LineageOS/android_hardware_lineage_compat/commit/353e696c1b54560fa53dd93a817e16cd2f2c2464)
records copying the VNDK-33 library and changing its SONAME. Both shipped ABI
copies exactly match our compatibility source prebuilts. Comparison with the
current checkout's VNDK-33 snapshot shows identical executable sections and
build IDs in each ABI; only dynamic/string/symbol-table metadata differs.
Therefore copying that snapshot again would not update executable crypto code.
A newer snapshot repository commit is not by itself evidence of fresher crypto.

The three consumers import 22, 65 and 21 symbols matching the old library.
`sk_delete` in keymaster helper is absent from the current platform exports.
More importantly, matching names do not establish ABI compatibility:

| ASN.1 item ABI, LP64 | VNDK-33 | Current platform |
| --- | --- | --- |
| `sizeof(ASN1_ITEM)` | 56 | 48 |
| `utype` offset/type | 8 / long | 4 / int |
| `templates` offset | 16 | 8 |
| `tcount` offset | 24 | 16 |

These sizes/offsets were compiled from the actual checked-out headers and agree
with the differing exported `ASN1_INTEGER_it` object sizes. Legacy consumers
use ASN.1 item functions and descriptors. A function alias cannot repair their
structure ABI. BoringSSL explicitly provides no stable API/ABI guarantee:
[upstream policy](https://boringssl.googlesource.com/boringssl/+/HEAD/README.md).

A credible replacement needs an identified ABI-compatible source baseline,
reviewed security backports, exported-data/layout checks and device credential,
keymaster/keystore/attestation and encrypted reboot/update regressions. No CVE,
patch freshness or exploitable condition is assigned from the filename alone.
The exact source revision behind these prebuilt bytes is not yet established.
Do not replace them with current `libcrypto.so` or alter credential data to make
a replacement appear to work.

### Protobuf and source-built shims

Lineage commit
[`9e8811a2`](https://github.com/LineageOS/android_hardware_lineage_compat/commit/9e8811a297036c370f7643813a3c733f6e442d86)
documents the four protobuf-3.9.1 ABI/full/lite prebuilts as originating from
`barbet-img-9269995.zip`. This establishes the maintainer's recorded provenance,
not an independent factory-image hash comparison. The platform source now has
`GOOGLE_PROTOBUF_VERSION=6033005`; it is not an automatic binary-compatible
replacement for 3.9.1-generated closed vendor code. Review ABI-preserving source
rebuilds/patch backports and the generated-message contracts before replacing it.

The crypto CBS shim and graphics shim are built from readable Lineage source.
The former restores small functions that modern headers inline. The latter
adapts removed signatures and waits for the release fence in old synchronous
unlock calls. Actual scaler imports do not use the shim's async overloads in
this scan. No device-facing defect in those exercised shim signatures was
demonstrated here; removing them would leave required imports unsatisfied.

## Runtime follow-up and boundaries

The owner enabled temporary Rooted debugging for the remaining inspection.
Metadata-only reads found 78 loaded programs and 97 maps, including socket
storage, ring buffers, a devmap hash and two mmap-flagged maps. The DMA-BUF
iterator and wakelock activate/deactivate links are present. These observations
establish instantiated objects, not exhaustive feature semantics or performance.

The generic `bpftool cgroup show` returned status255 without usable attachment
results. A small native helper using only `BPF_PROG_QUERY` then queried the
existing root cgroup. All 14 selected hooks succeeded with one attached program
each: ingress/egress, socket create/release, IPv4/IPv6 bind/connect,
IPv4/IPv6 sendmsg/recvmsg, getsockopt and setsockopt. Nothing was loaded,
attached, detached, pinned or updated by the helper; it was removed afterward.
This is stronger evidence for those backports than source declarations alone.

Mappings from 13 selected Android/native hardware services show actual use:

| Service | Legacy library mapped |
| --- | --- |
| Gatekeeper and Samsung Keymaster | 64-bit `libcrypto-v33.so` |
| Widevine DRM | 32-bit CBS shim and protobuf lite3.9.1 |
| Sensor multihal | 64-bit protobuf lite3.9.1 |
| Samsung camera provider | 32-bit protobuf full/lite3.9.1 |

Third-party app maps and application data were not inspected. The UI shim was
not mapped in these sampled idle services; its four actual scaler dependencies
remain, and no camera/scaler workload was launched to prove dynamic use or
non-use. No credential operations, media session or service restart was induced.

The available tag-filtered/kernel logs contained no retained startup/listener
evidence. They cannot explain the absent AMS attachment or establish a fresh
loader startup pass. No OOM/memory-pressure test or map-content dump was run.

Final checks confirm the same build1793018822, bootcomplete, encrypted data,
enforcing SELinux, normal ADB UID2000, Rooted debugging off and both temporary
helpers absent. Tracepoint formats were initially readable without root. The
public release and source pins are unchanged.

Keep the public release/source pins unchanged during this audit. Next work
should isolate the OOM tracepoint repair from changes to library identity or
the global version override, retaining current recovery/rollback and all prior
network, accounting, DMA-BUF, credential and hardware regressions.

## Subsequent isolated candidate build

The owner subsequently authorized building the suggested fixes. Candidate
**1793039898**, kernel [`f0f9fc679`](https://github.com/tylxr59/android_kernel_samsung_gta4xlve/commit/f0f9fc67947a37d2e530367c227d228ec5d966d2),
backports the OOM tracepoint extension and call site from the reviewed Android
common patch, adapting include placement to4.14 while retaining credential
references and the existing task/mm lifetime requirements. No other project,
kernel configuration, version override or legacy library changes are included.

Full build, strict VINTF, compiled tracepoint-layout/BTF/config/default checks
and private-key signing/OTA verification passed; see [testing](testing.md).
This is a built candidate, not an installed or hardware-verified fix. Installed
and public1793018822, OTA feed and release pins remain unchanged. The earlier
statement that no patch was applied describes the audit stage before this build.
