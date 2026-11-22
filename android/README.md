# PeakCut Android

## Native foundation

- Android video picker and preview.
- Start/end-time MP4 clip export using MediaExtractor and MediaMuxer.
- Sherpa-ONNX Android runtime, restricted to arm64-v8a and x86_64.
- Multilingual Whisper tiny model downloader and app-private model storage.
- Hindi-default ASR service accepting mono Float32 PCM at 16 kHz and returning transcript text plus token timestamps.

The Whisper model is downloaded on demand (roughly 100 MB of model data) and is not bundled into the APK.

## Build

Open this `android/` folder in Android Studio, or run `gradle :app:assembleDebug` with JDK 17 and Android SDK 35 installed.

The debug APK is generated at `app/build/outputs/apk/debug/app-debug.apk`. GitHub Actions builds it on pushes to `android-apk` and uploads an artifact.

## Remaining integration

The current screen does not yet expose transcription. The next step is Android MediaCodec audio extraction/resampling into mono 16 kHz Float32, then wiring Whisper output into caption editing and video rendering. AI highlight selection, live stream capture, creator workspaces and social posting still need to be ported from the Python server and tested on a physical Android device. This is an early native port, not full PeakCut feature parity.
