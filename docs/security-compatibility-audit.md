# Remaining compatibility and security audit

Baseline: public **1792961358**, device **038bb20**, kernel **dc07aa16f**,
vendor **1c0a6f2**, Pixel HAL **d4f83b6**. Four maintained source checkouts are
clean and match the released manifest; the actual live kernel configuration
matches the signed target files. This is a focused audit, not a full CVE,
CTS/VTS or penetration-test certification. Official-device submission is not
the owner's goal; priorities here are safe, useful Android behavior on SM-P613.

No ROM source, image, sysctl or persistent tuning changed. No ROM build, installation,
flashing or reboot. Temporary Rooted debugging was used only for inspection and
restored off through the official service. Temporary native catalog clients
were removed; their crash records were deliberately preserved as evidence.
Raw logs, policy/process snapshots and reproducer details remain private.

## Actionable findings

| Priority | Finding | Observed impact | Recommended next step |
| --- | --- | --- | --- |
| 1 | NDK codec-catalog capability lifetime bug | A valid public API lookup succeeds, but the query client aborts during library/process cleanup. A minimal, header-typed client reproduces it. | Fix the capability-object ownership in the pinned framework library; test normal teardown with sanitizers and on-device. |
| 2 | Kernel wakelock BPF program uses unsupported atomics | Loader returns EINVAL; suspend service reports no aggregate kernel-wakelock duration. | Review a genuine verifier/core/ARM64-JIT atomic backport, or capability-gate this optional feature until supported. |
| 3 | BPF version override overstates the legacy kernel | Actual4.14.357 is selected as5.10.239 for version-dependent BPF paths. Networking and DMA-BUF work, but this is not blanket5.10 capability coverage. | Replace assumptions incrementally with real feature checks/backports. Do not remove the override globally without boot/network testing. |
| 4 | Additional kernel/sysctl hardening is available | Four filesystem protected_* sysctls are0; REFCOUNT_FULL is off; old FORTIFY is unavailable with Clang; BPF JIT blinding is off. | Evaluate separate, bounded candidates with compatibility/performance tests. No proven exploit is claimed from these settings alone. |

### NDK codec catalog

A read-only enumeration returned48 codec entries, including hardware AVC/HEVC
and software H.263/MPEG4. The client then aborted in libmediandk capability-object
cleanup. A smaller client using the checked-out public NDK headers and one valid
codec lookup returned success before the same teardown failure. Bypassing normal
process teardown is a diagnostic control only; it is **not** the proposed fix.
Source inspection identifies incorrect ownership of performance-point objects.
Detailed reproducers and traces are retained privately for the correction.

The observed fault is in the calling process. System server, audioserver, audio
HAL and media-server PIDs stayed unchanged. The initial crash buffer was empty;
the audit's final crash buffer contains the owned client reproductions and was
not cleared. There is no demonstrated cross-app compromise, privilege escalation
or normal playback failure from this result. Nevertheless this is a real
framework memory-lifetime defect, not an XML-label problem or a reason to disable
Scudo. Do not advertise a fix until the real library is corrected and tested.

### BPF compatibility

The actual shipped wakelock object contains atomic compare/exchange and
fetch-add instructions. The pinned verifier only accepts legacy XADD with a zero
immediate, and its ARM64 JIT implements only that older operation. This is a
concrete incompatible instruction set, consistent with the live EINVAL rejection;
additional compatibility issues may become visible after it is addressed.
Traditional per-source kernel wakeup statistics remain available. Missing total
duration is an observability gap, not proof that hardware suspend is broken or
that fixing the counter will save battery.

The fuseMedia loader also tries to load an unavailable FUSE-BPF backend.
Live ro.fuse.bpf.is_running is false. MediaProvider/vold already detect the absent
kernel feature and select the non-BPF path. Storage/mount records show that
fallback in use. A capability gate in the loader is a reasonable cleanup;
backporting an entire filesystem backend just to silence this log is not the
preferred first change. [AOSP storage design](https://source.android.com/docs/core/storage/scoped)
documents the normal FUSE-based scoped-storage path.

Current working DMA-BUF iteration and critical network BPF are separate from
these remaining optional programs. Do not regress them by setting a blanket
kernel-version or privilege switch.

## Hardening: actual settings and boundaries

- Live ASLR mode2, kptr_restrict2 and dmesg_restrict1. Ordinary shell reads of
  kallsyms/dmesg are denied. Debugfs and /dev/mem are not available.
- CFI is enforcing; KPTI, PAN, strict kernel/module RWX, strong stack protector,
  slab freelist randomization/hardening, zero-initialized stacks/allocations,
  hardened usercopy and forced module signatures are enabled. Kernel vulnerability
  sysfs reports mitigations/not-affected as documented; those are not independent
  hardware vulnerability certifications.
- Live protected_hardlinks, protected_symlinks, protected_fifos and
  protected_regular are all0. These are useful defense-in-depth candidates for
  shared-directory/link attacks. Android's sandbox/storage model also matters;
  no accessible exploit path was demonstrated. See the
  [kernel filesystem sysctl documentation](https://docs.kernel.org/6.1/admin-guide/sysctl/fs.html).
- REFCOUNT_FULL is unset and this configuration does not select an architecture
  replacement; the header falls back to ordinary atomic refcounts. Full refcount
  checking is worth testing against legacy drivers.
- FORTIFY_SOURCE is not enabled. Its old Kconfig explicitly excludes Clang for
  historical compiler issues. A compatible modern implementation/backport is the
  appropriate investigation; do not simply delete the compiler gate.
- BPF JIT is enabled, bpf_jit_harden0 and bpf_jit_kallsyms1. Constant blinding is
  optional defense in depth; exporting JIT symbols is privileged. kptr restrictions
  and SELinux already restrict access. Test any change with networking, DMA-BUF
  and profiling. [Kernel JIT controls](https://docs.kernel.org/next/admin-guide/sysctl/net.html)
  describe the hardening/performance tradeoff.

### App access is not equivalent to a permissive sysctl

The actual live policy was queried with the Android source-matched libsepol:
532 access decisions across ordinary/legacy app, isolated-app, shell and service
domains. Sampled ordinary/isolated app domains are denied BPF program loading,
map creation/access, perf_event access and SYS_ADMIN/SYS_PTRACE/SYS_RAWIO grants.
All21 sampled application/isolated UID processes had zero effective capabilities.
These are policy/snapshot results, not an instrumented untrusted-app exploit test.

unprivileged_bpf_disabled is0, but the above SELinux gates still apply. Blindly
setting it nonzero is unsafe here: the old syscall checks privilege before
command dispatch, including operations used by legitimate system services.
A compatible restriction must distinguish trusted pinned-map consumers.

perf_event_paranoid is-1 as configured by AOSP Perfetto; kernel SELinux perf hooks
are present and the sampled app-domain decisions deny access. Do not disable
profiling globally as a substitute for understanding those controls.

ART needs userfaultfd. The kernel's kernel-fault mode is gated by
UFFD_USER_MODE_ONLY, SYS_PTRACE and the vm.unprivileged_userfaultfd sysctl.
Its source default is0; this audit did not verify that live value because the
correct VM path is denied to ordinary shell after privileged cleanup. Do not
confuse the missing /proc/sys/kernel path with a missing kernel restriction.

## Known limitations to retain explicitly

- **Boot integrity:** vbmeta flags3 remain. The previous verification-enabled
  experiment was rejected by Samsung key trust; original metadata was restored.
  OTA signatures authenticate updates, not locked boot-time integrity. Do not
  repeat a flags-only experiment or relock. No supported custom-key enrollment
  is established. [Prior evidence](build-exceptions-audit.md#verified-boot-experiment-blocked-by-samsung-trust).
- **Closed vendor code:** live vendor patch2025-05-01 versus platform2026-10-01.
  No firmware refresh or exhaustive closed-code CVE audit was performed here.
  Shared-maintainer blob provenance and ABI shims remain necessary boundaries;
  platform security dates cannot update closed firmware automatically.
- **Development policy:** su/backuptool/qti-testscripts remain compiled permissive
  domains. None was active in the normal snapshots; only the intentional temporary
  audit su domain appeared during rooted inspection. No app-facing su executable
  was present. This is not global permissive SELinux or installed app-root.
- **Legacy ABI adapters:** libcrypto-v33/libcrypto_shim/libui_shim and protobuf
  compatibility libraries preserve old blob APIs. They merit lifecycle/provenance
  review, not blind deletion. libcrypto-v33 is a prebuilt VNDK33 binary in
  hardware/lineage/compat; rebuilding the platform's current crypto library does
  not refresh it automatically. The small CBS crypto shim and UI shim are built
  from compatibility source. A dependency/provenance review is appropriate; this
  audit does not assign a CVE or patch age to that prebuilt. Previous restored
  ELF checks stay enabled.

## Checks that did not identify a new defect

The three removed BUILD_BROKEN switches and vendor check_elf_files:false
exemptions remain absent. Strict VINTF with authentic kernel metadata and
existing-key signing/OTA checks passed for the current release.

A scan of2,814 ARM ELF executables/libraries in the signed system/vendor family
found no writable-executable LOAD segments or executable GNU_STACK markers.
Three static system utilities use ET_EXEC; these are platform build artifacts,
not newly imported non-PIE vendor blobs. That classification does not certify
all ELF contents or ASLR behavior. Fourteen other-architecture firmware objects
were outside this ARM userspace scan; APEX payloads were not rescanned here.

The remaining legacy MPEG4/H263 OMX metadata does not mean those formats are
unavailable: the live catalog advertises C2 software alternatives. Full encode/
decode and DRM tests remain separate. Legacy Android/SoC service noise alone
is not a reason to remove vendor components.

lpm_levels.sleep_disabled reads N, confirming it is not currently forcing sleep
off. The connected/active snapshot had no suspend attempts, so it is not an
endurance/suspend test. Keep the owner's encouraging overnight report distinct
from a controlled battery measurement. No new ROM power improvement is claimed.

## Next implementation order

1. Correct NDK capability ownership and validate public API normal teardown.
2. Resolve the wakelock BPF instruction mismatch with real support or truthful
   capability selection; preserve working networking/DMA-BUF.
3. Add a truthful FUSE-BPF load gate without changing working storage behavior.
4. Test filesystem protections and full refcounts separately, then consider
   Clang-compatible FORTIFY/JIT hardening with measured compatibility costs.
5. Continue real hardware/codec/storage/endurance testing; avoid performance
   tuning based only on noisy logs or desktop hardening checklists.
