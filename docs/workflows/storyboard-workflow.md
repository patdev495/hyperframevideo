# Storyboard Workflow

The Storyboard phase starts after Voiceover generation. It turns an approved `SCRIPT.md` and its `voiceover.json` timing manifest into a `STORYBOARD.md` that describes each scene's visual timing, narration, on-screen text, and visual direction.

This phase is CLI-first and operates on an existing Production Run under `.runs/<run-id>/`.

## 1. Approve the Script and Generate Voiceover

Before running storyboard generation, the Production Run must have:

- `SCRIPT.md` with `Status: approved` in its header.
- `voiceover.json` written by the Voiceover Provider phase.

The storyboard command refuses `Status: draft`, a missing status, unsupported status values, missing `SCRIPT.md`, and missing `voiceover.json`.

## 2. Run Storyboard Generation

Run the storyboard command with the Production Run ID:

```powershell
hyperframe-video --storyboard <run-id>
```

The command reads `.runs/<run-id>/SCRIPT.md` and `.runs/<run-id>/voiceover.json`, extracts script scenes and voiceover timing, aligns them by segment ID, computes cumulative start times, and writes `STORYBOARD.md`.

## 3. Generated Files

On success, the Production Run contains:

```text
.runs/<run-id>/
|-- SCRIPT.md
|-- voiceover.json
|-- voiceover/
|   |-- segment-001.wav
|   `-- segment-002.wav
`-- STORYBOARD.md
```

The command fails instead of overwriting when `STORYBOARD.md` already exists. This prevents stale visual plans from being silently replaced.

## 4. Storyboard Contract

`STORYBOARD.md` is the visual instruction contract for future HyperFrames composition generation. Each scene in the storyboard maps to one voiceover segment and includes:

- **Timing**: start time and duration from `voiceover.json`.
- **Script fields**: narration, on-screen text, purpose, and facts used from `SCRIPT.md`.
- **Visual direction**: a placeholder scoped to the current Visual Treatment (default `ai-modern`).

The generator is deterministic — the same inputs always produce the same `STORYBOARD.md`, making it testable and cacheable.

## Scope Boundary

This phase does **not** generate HyperFrames composition files, MP4 output, asset downloads, B-roll search, image generation, or web UI controls. It only validates approvals and inputs, aligns scenes with timing, and writes the storyboard markdown that later rendering phases can consume.
