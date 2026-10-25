# Bluetooth media routing investigation

## Baseline: released1792944959

The owner reported AirPods Pro 2 pair and connect, but music/video stays on the
tablet speakers. This is the first real Bluetooth audio test; earlier discovery
checks did not establish playback. Private device logs show A2DP connected and
AAC stereo44.1kHz negotiated. Audio policy nevertheless rejects making the A2DP
device available, and its available outputs lack an A2DP media device. This is
an audio-service/routing failure after pairing, not evidence of a radio defect.

The current source builds `audio.bluetooth.default` and the old HIDL2.0 provider
implementation, without declaring that provider in VINTF. Modern Bluetooth's
`HalVersionManager` tries AIDL, then enumerates declared HIDL2.1/2.0 instances.
The live AIDL provider is absent and the HIDL2.0 provider is running but absent
from the declared list. The audio service deliberately supports loading
`android.hardware.bluetooth.audio-impl`, which registers the current AIDL
provider; this library also installs its VINTF fragment. Existing Bluetooth audio
session utilities bridge the legacy audio HAL to AIDL sessions.

## Candidate, not yet hardware verified

[Device038bb20](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/038bb20)
adds the existing AOSP `android.hardware.bluetooth.audio-impl` package. No new
custom audio code, XML route changes, speaker calibration, kernel changes,
privilege relaxations or pairing resets. Exact candidate inputs are
[resolved manifest](../manifests/candidates/bluetooth-audio-20261025.xml) and
[fork manifest](../manifests/candidates/bluetooth-audio-forks-20261025.xml).

The full signed candidate is building. Strict VINTF, installed32-bit library and
AIDL fragment, unchanged kernel/config/audio policy/SELinux/USB/thermal inputs,
signature continuity and no-wipe installation must pass before calling this
fixed. Then verify live provider registration, A2DP output availability, actual
playback heard by the owner, pause/resume, reconnect and speaker switching.
SCO microphone/call audio and other headsets/codecs need separate evidence.
The public release/feed remain1792944959; no new release requested.
