# Storyboard Artifact

The Storyboard Artifact is generated after Voiceover generation from an approved `SCRIPT.md` and its `voiceover.json` timing manifest. It translates each voiceover segment into a visual scene with timing, narration, on-screen text, and visual direction.

## Files

```text
.runs/<run-id>/
`-- STORYBOARD.md
```

`STORYBOARD.md` is written at the top level of the Production Run alongside `SCRIPT.md` and `voiceover.json`.

## Scene Fields

Each `## Scene N` block in `STORYBOARD.md` contains the following fields:

| Field | Source | Description |
|-------|--------|-------------|
| Segment ID | Script order | Stable identifier such as `segment-001` |
| Order | Script order | One-based scene position |
| Start Time | Cumulative from voiceover | When the scene begins, in seconds |
| Duration | `voiceover.json` | Spoken duration of the narration, in seconds |
| Audio | `voiceover.json` | Relative path to the generated `.wav` file |
| Narration | `SCRIPT.md` | The spoken narration text |
| On-screen Text | `SCRIPT.md` | Text that should appear on screen |
| Purpose | `SCRIPT.md` | Why this scene exists (optional) |
| Facts Used | `SCRIPT.md` | Verifiable facts referenced (optional) |
| Visual Direction | Visual Treatment | Placeholder for future composition instructions |

## Example Output

```markdown
# Storyboard

Run ID: run-001
Visual Treatment: premium-news
Total Duration: 3.50s
Source Artifacts: SCRIPT.md, voiceover.json

## Scene 1

- **Segment ID:** segment-001
- **Order:** 1
- **Start Time:** 0.00s
- **Duration:** 1.50s
- **Audio:** voiceover/segment-001.wav
- **Narration:** First scene narration.
- **On-screen Text:** First screen text.
- **Purpose:** Introduce the topic.
- **Facts Used:** Fact A about the topic.
- **Visual Direction:** [premium-news]
```

## Rules

- `STORYBOARD.md` depends on an approved `SCRIPT.md` and existing `voiceover.json`.
- The command refuses to run if `STORYBOARD.md` already exists.
- Start times are computed by accumulating `duration_seconds` from `voiceover.json`.
- The default Visual Treatment is `premium-news` unless `SCRIPT.md` declares another value.
- `audio_path` values are relative to the Production Run directory so the run remains portable.
- This artifact is the visual instruction contract for future HyperFrames composition generation.

## Scope Boundary

This artifact does **not** include HyperFrames composition files, MP4 output, asset downloads, B-roll search, image generation, or web UI controls. It is a deterministic markdown representation of the approved script aligned with voiceover timing.
