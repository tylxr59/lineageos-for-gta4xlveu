# Speaker audio audit

Initial read-only inspection on 2026-10-23 of release `1792787032`, device `eb9bc69`,
kernel `75a416868`, vendor `4388d72`. No sound settings, gain, calibration,
firmware, or tablet security settings were changed. Rooted debugging stayed off.

The initial snapshot below is retained separately from the later authorized
experiments and findings. The public release has not changed.

## Initial configuration and runtime evidence

- The device builds the Qualcomm `audio.primary.atoll` HAL and audio/effects
  HIDL 7 implementations. Policy exposes a stereo speaker output at 48 kHz.
  This is a route capability, not an acoustic channel-separation measurement.
- `mixer_paths.xml` maps `speaker` to `spk`, enabling left and right TAS256X
  amplifier inputs. The kernel contains TI SmartAmp/calibration support, and
  the live `/sys/class/tas25xx/{calib,valid,bigdata}` interfaces exist.
- The installed effects configuration, legacy effects configuration, both
  platform-info XML files, policy XML, and mixer XML match source SHA256 hashes.
  Installed `Speaker_cal.acdb`, `General_cal.acdb`, and `Global_cal.acdb` also
  match the maintained vendor blobs: nine files compared in total.
- The vendor ACDB loader references `/vendor/etc/audconf/OPEN`, where these
  calibration files are installed. Retained runtime logs show speaker routing
  and calibration requests for ACDB device 14, app type `0x11131`, 48 kHz.
  Device 14 agrees with `audio_platform_info_intcodec.xml`; the other platform
  XML uses 15. Those different alternatives alone do not demonstrate a defect.
- Logs show an AFE topology lookup returning `0x112fc` and volume calibration
  submission. They also repeatedly report
  `ACDB_CMD_GET_AFE_INSTANCE_COMMON_TABLE_SIZE Returned = -19` and
  `ACDB AFE returned = -19`. The significance is unresolved: this does not
  establish that the entire calibration database failed or that the errors
  explain perceived sound quality. Boot-time database initialization messages
  were not present in the retained filtered buffer.
- The effects XML registers EQ, bass boost, virtualizer, loudness enhancement,
  dynamics processing and Qualcomm effects; referenced effect libraries are
  present in `/vendor/lib64/soundfx`. Automatic music postprocessing specifies
  a volume-listener helper, rather than an always-applied speaker EQ or dynamics
  preset. DSP processing below AudioFlinger may still be active.
- Dolby DS2 is disabled in the maintained vendor properties, and this effects
  XML has no Dolby effect registration. Enabling a property alone would not
  supply a working Dolby implementation or model-specific tuning.
- Lineage AudioFX is installed. Its source supports separate speaker settings
  and session-based EQ, including a default Small Speakers preset when a
  five-band backend is available. Its UI disables bass boost and virtualizer
  controls for built-in speakers. These are source capabilities, not a readback
  of the owner's private AudioFX preferences or proof of coverage in every app.

## Limits and next checks

The snapshot had zero AudioFlinger effect chains; no controlled playback session
was started. This cannot establish whether AudioFX attaches correctly during
playback, nor whether DSP/amplifier processing is absent. Normal shell access
cannot read TI calibration/validation status or ALSA mixer controls. Configuration
flags enabling Qualcomm speaker protection do not prove live TI protection.
No factory-calibration operation was invoked and no EFS data was changed.

Before adding processing:

1. Capture a controlled speaker playback session and check loaded effects,
   routing, sample rate, calibration requests and errors together. Include both
   ordinary PCM and supported offload playback; compare headphones separately.
2. Inspect TI amplifier calibration/protection status with suitable diagnostic
   access, preserving factory EFS calibration and returning rooted debugging
   to off afterward. Never trigger calibration merely to read status.
3. Compare the failing ACDB query and selected topology with a compatible known
   working reference before changing device IDs, calibration files or HAL code.
   Do not infer a fix merely from different generic platform XML values.
4. Establish a listening/measurement baseline at matched volume, then evaluate
   a reversible speaker-only EQ preset. Check dialogue, music, peak distortion,
   stereo separation and behavior across volume levels. Frequency-response
   claims require acoustic measurements; no measured EQ curve exists yet.

The audit establishes that vendor calibration assets and a functioning
calibration request path exist. Complete Samsung processing parity, protection
operation and an audible quality improvement remain unverified. No audio ROM
change or release is justified by this inspection alone.

## Authorized follow-up: TI processing proof

Subsequent controlled tests used temporary rooted debugging with SELinux
remaining enforcing. The owner's installed release was retained, and each
bounded prototype restored the original audio libraries and profile afterward.
No amplifier gain, protection threshold, DSP firmware or calibration value was
changed, and no new factory calibration was performed.

The factory `/efs/tas25xx` files carried an obsolete stored SELinux label that
appeared as `unlabeled` under this policy. The existing `audio_efs_file` policy
already permits the required narrow audio-HAL access. Restoring the existing
path labels fixed these access denials; SHA256 checks confirmed all four file
contents unchanged. A device init change repeats this label restoration after
mounting data. Reported factory speaker resistance is 6.15 and 5.82 ohms, with
28°C calibration temperatures. A zero calibration-operation status means no
new calibration was run, rather than a demonstrated calibration failure.

The installed calibration database maps ACDB14 to topology `0x112fc`, while
ACDB15 selects TI receive topology `0x1000fc01`. Feedback device102 uses TI
transmit topology `0x1000fd01`. The older profile14 setting predates this port:
[the upstream 2023 change](https://github.com/gta4xlve-dev/android_device_samsung_gta4xlveu/commit/52828a524a1c5954b012b0e2a513492e33cfbf5e)
did not include a rationale.

Simply switching to15 caused silence and AFE port-start failures. Changing
bit width or channel count did not fix it. A separate process initializing its
own ACDB loader also produced misleading results and allocation conflicts;
that approach was rejected.

The successful prototype reuses the audio HAL's existing initialized ACDB
loader, submits device102 as **input**, opens stereo feedback capture through
MultiMedia2/PCM1 at48kHz, and registers QUIN feedback TX `0x1017` with speaker
RX `0x1016` through the kernel's existing AFE feedback API. Both TI topologies
started, the receive path unmuted, and the earlier TI parameter failures were
absent in that pass. The owner reported both speakers working and sound
substantially clearer and fuller against the original, with some bright treble
and limited bass. This is a listening result, not an acoustic measurement or
proof of Samsung processing parity or complete protection behavior.

A further prototype using the HAL's existing external-hardware playback hooks
opened feedback for three consecutive playback cycles and closed PCM1 after
each standby interval. No continuous idle capture is needed. Source integration
and failure/route handling are under development; these experiments are **not**
a shipped ROM fix. The published OTA feed remains unchanged. Headphone/Bluetooth
transitions, concurrent capture, offload coverage, suspend power, thermal
protection and a signed local update still require validation before release.

Preserve the original profile14 fallback and existing factory tuning. Do not
add bass boost, amplifier gain or proprietary coefficient edits based only on
this subjective comparison.

## Dolby follow-up: controlled offload prototype

The installed ADSP includes `capi_v2_Dolby_Atmos` / DAP processing code and reads
the existing vendor `dax_param.bin`. The global ACDB maps app11130 to ASM
playback topology `0x10005000`, which contains Dolby module `0x10001fd0`.
The Samsung kernel already exposes a three-value `DA data` mixer control:
enable, output device and profile. It sends parameter `0x10001fd1` to the
MultiMedia4/ASM frontend3 session. This Samsung interface does not depend on
the absent generic CAF `libhwdaphal.so` controller.

The published policy exposes compressed offload for HDMI, with no MP3 speaker
route. An authorized, bounded test temporarily added an MP3 offload mix port
and speaker route through a bind-mounted policy file. AudioFlinger confirmed
an active OFFLOAD thread, stereo48kHz MP3 and built-in speaker output. Enabling
and disabling device2/profile0 returned success, and the kernel recorded the
exact intended payloads. Tinyalsa integer arrays use `long` elements; an initial
helper using `int` was rejected and corrected before accepting the result.

The first synthetic listening sample had abrupt note-boundary discontinuities.
The owner heard clicks and increased volume. A smoothed replacement removed
the clicks; the owner described Dolby as mainly louder. A further comparison
used a repeated excerpt from a real song supplied by the owner, again with
Dolby OFF/ON at20-second intervals. The owner again reported mainly increased
volume. Test playback was stopped promptly when the owner requested a lower
level; media volume was lowered to3/15 and the player gain reduced further.
The downloaded song, diagnostic APK and raw evidence remain private artifacts.

This demonstrates an operational Dolby control path for the diagnostic offload
stream, not a demonstrated fidelity improvement or a complete Android Dolby
implementation. The trials were not acoustically level-matched and do not prove
that Dolby has no other effect, or that every profile behaves the same. Ordinary
YouTube playback is not covered by this offload-only prototype. Broader support
would require playback-route/lifecycle integration, correct volume handling,
and appropriate Android controls, followed by listening and power tests.

The temporary policy was detached, diagnostic playback stopped, audio services
restarted and the test app/helpers removed. No Dolby setting was retained.
Final checks confirmed normal ADB UID2000, Rooted debugging disabled, SELinux
enforcing and the diagnostic app absent. Media volume remains3/15 at the
owner's request. The installed ROM and public OTA feed remain unchanged. TI integration stays
paused at the owner's request; its source candidates are saved locally. The
kernel routing control compiled, but the production audio-library build was
intentionally stopped during graph generation. No new audio ROM was built,
installed or published. Neither experiment establishes a measured acoustic
quality ceiling for this device.
