# Speaker audio audit

Read-only inspection on 2026-10-23 of release `1792787032`, device `eb9bc69`,
kernel `75a416868`, vendor `4388d72`. No sound settings, gain, calibration,
firmware, or tablet security settings were changed. Rooted debugging stayed off.

## Confirmed configuration and runtime evidence

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
