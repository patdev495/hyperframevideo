Status: ready-for-agent

# Implement VieNeu Voiceover Provider

## Parent

`.scratch/voiceover-provider/PRD.md`

## What to build

Implement the first real local-first **Voiceover Provider** behind a thin provider interface using VieNeu-TTS through the `vieneu` Python SDK. It accepts typed voiceover segments and writes `.wav` files into the **Production Run** voiceover audio directory, returning typed outputs with segment ID, audio path, duration seconds, provider name, voice configuration, and warnings.

Automated tests should use a fake VieNeu SDK/provider and must not run real model inference or download models. The implementation should make VieNeu an optional or isolated runtime dependency if feasible, so ordinary test runs and non-voiceover CLI flows do not require TTS setup.

## Acceptance criteria

- [ ] A `VoiceoverProvider` interface or protocol exists with a small stable method.
- [ ] The VieNeu provider accepts ordered voiceover segments.
- [ ] The provider writes one `.wav` file per segment through the VieNeu SDK.
- [ ] The provider returns typed output metadata for each segment.
- [ ] Provider metadata includes `provider_name` and selected VieNeu voice configuration.
- [ ] Missing VieNeu installation or runtime setup produces a readable diagnostic.
- [ ] No API keys, OS speech settings, or real HyperFrames installation are required.
- [ ] Tests use a fake VieNeu SDK/provider and verify files/metadata without model downloads.

## Blocked by

- `.scratch/voiceover-provider/issues/03-extend-production-run-store-for-voiceover-artifacts.md`
