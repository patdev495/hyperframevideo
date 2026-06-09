# Voiceover Artifacts

Voiceover artifacts are generated after Script Approval from the `Narration:` lines in `SCRIPT.md`.

## Files

```text
.runs/<run-id>/
|-- voiceover.json
`-- voiceover/
    |-- segment-001.wav
    `-- segment-002.wav
```

`voiceover.json` is written at the top level of the Production Run. Audio files live in the run-owned `voiceover/` directory.

## Manifest

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

## Rules

- `audio_path` is relative to the Production Run directory.
- `segment_id` is stable and based on narration order.
- `order` is one-based script order.
- `duration_seconds` is measured from the generated `.wav` file.
- `warnings` records provider-specific non-fatal issues.
- Future storyboard work consumes this manifest as the audio and timing contract.
