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

## Candidate1792961358: media playback verified

[Device038bb20](https://github.com/tylxr59/android_device_samsung_gta4xlveu/commit/038bb20)
adds the existing AOSP `android.hardware.bluetooth.audio-impl` package. No new
custom audio code, XML route changes, speaker calibration, kernel changes,
privilege relaxations or pairing resets. Exact candidate inputs are
[resolved manifest](../manifests/candidates/bluetooth-audio-20261025.xml) and
[fork manifest](../manifests/candidates/bluetooth-audio-forks-20261025.xml).

The full signed candidate **1792961358** passed build, strict VINTF, installed
32-bit library/AIDL-fragment checks, persistent-key component/whole-OTA signature
verification and a no-wipe installation. Boot and DTBO images are byte-identical
to1792944959; the actual kernel/config, audio policy, SELinux, USB and thermal
service remain unchanged. Android boot, encrypted data/test-file persistence,
setup flags, enforcing SELinux, UID2000, Rooted debugging off and empty crash
buffer passed.

The AIDL provider is registered; A2DP now appears as an available media output.
The owner heard playback through AirPods Pro2. Captured logs confirm AAC with
A2DP_SOFTWARE_ENCODING_DATAPATH and successful stream start/suspend, with no
new observed audio/Bluetooth AVCs. This establishes media playback on this
headset, not hardware offload, energy efficiency, all codecs or all devices.
The owner also confirmed case/disconnect fallback to speakers, separate device
volume levels and successful playback after reconnecting. The reconnected route
appears in policy, with no recurrence of the original A2DP rejection and no
crash-buffer entries. Actual matching recovery/config and full boot/DTBO/recovery
partition hashes passed; prior vbmeta is unchanged. Final recovery-menu return to Android and owner unlock passed. Encrypted data,
setup/test-file persistence, enforcing SELinux, UID2000, Rooted debugging off
and empty crash buffer passed; the provider remains registered after reboot.
The owned persistence marker is removed. No temporary app, logger, audio
override or root helper was installed. Rooted debugging stayed off throughout.
SCO microphone/call audio and other headsets/codecs need separate evidence.
The public release/feed remain1792944959; no new release requested.


## Comparison with maintained LineageOS device integration

The same AOSP provider package is included by LineageOS
[Xiaomi SM6150 common](https://github.com/LineageOS/android_device_xiaomi_sm6150-common/blob/lineage-23.2/sm6150.mk)
and [Pixel4/coral](https://github.com/LineageOS/android_device_google_coral/blob/lineage-23.2/device-common.mk)
on lineage-23.2. This supports the integration choice; it does not replace
SM-P613 build and actual playback tests or establish identical vendor stacks.
