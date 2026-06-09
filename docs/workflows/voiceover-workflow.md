# Voiceover Workflow

The Voiceover Provider phase starts after Script Approval. It turns the approved `Narration:` lines in a Production Run's `SCRIPT.md` into audio files and a `voiceover.json` manifest.

This phase is CLI-first and operates on an existing Production Run under `.runs/<run-id>/`.

## 1. Approve the Script

Open `.runs/<run-id>/SCRIPT.md` and confirm that the header contains:

```text
Status: approved
```

The voiceover command refuses `Status: draft`, a missing status, unsupported status values, missing `SCRIPT.md`, and approved scripts without `Narration:` lines.

## 2. Run Voiceover Generation

Run the voiceover command with the Production Run ID:

```powershell
hyperframe-video --voiceover <run-id>
```

The command reads `.runs/<run-id>/SCRIPT.md`, extracts each `Narration:` line in script order, and assigns stable segment IDs such as `segment-001`.

## 3. Generated Files

On success, the Production Run contains:

```text
.runs/<run-id>/
|-- SCRIPT.md
|-- voiceover.json
`-- voiceover/
    |-- segment-001.wav
    `-- segment-002.wav
```

The command fails instead of overwriting when owned voiceover artifacts already exist, such as `voiceover.json` or the `voiceover/` directory.

## 4. Manifest Contract

`voiceover.json` is the timing and audio contract for future storyboard work. Future `STORYBOARD.md` generation can use it to align visual beats with generated narration audio.

The manifest records the provider and one entry per narration segment:

```json
{
  "provider_name": "vieneu",
  "segments": [
    {
      "segment_id": "segment-001",
      "order": 1,
      "narration_text": "Approved spoken narration.",
      "audio_path": "voiceover/segment-001.wav",
      "duration_seconds": 1.25,
      "warnings": []
    }
  ]
}
```

`audio_path` values are relative to the Production Run directory so the run remains portable.

## 5. VieNeu-TTS Provider

VieNeu-TTS is the first real Voiceover Provider target. The adapter loads the VieNeu Python SDK only when the voiceover command needs it, so Direct Source and Discovery Request workflows do not require VieNeu setup.

VieNeu-TTS may need local runtime setup, model downloads, and compatible native dependencies before it can synthesize audio. Missing SDK installation or runtime setup failures are reported as readable CLI diagnostics. The first provider path is intended to prove the artifact contract and local-first workflow; it should not be treated as a promise of production-quality speech without local validation.

## Scope Boundary

This phase does not generate `STORYBOARD.md`, HyperFrames compositions, MP4 output, or web UI controls. It only validates Script Approval, extracts narration, generates voiceover audio, and writes the manifest that later phases can consume.
