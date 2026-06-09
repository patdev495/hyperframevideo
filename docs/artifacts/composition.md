# HyperFrames Composition Artifact

The HyperFrames Composition Artifact is generated after the Storyboard phase. It translates `STORYBOARD.md`, `voiceover.json`, and voiceover audio into a `composition/index.html` file that HyperFrames can render to MP4.

## Files

```text
.runs/<run-id>/
`-- composition/
    |-- index.html
    `-- voiceover/
        |-- segment-001.wav
        `-- segment-002.wav
```

`composition/index.html` is the main HyperFrames composition. `composition/voiceover/` contains copies of the generated audio files with relative paths matching the HTML.

## Composition Format

`index.html` is a standalone HTML file with a single `<div id="stage">` wrapping all scenes. Each scene is a `<div>` with:

- `data-composition-id`: the Production Run ID
- `data-start`: start time in seconds (cumulative from voiceover timing)
- `data-duration`: duration in seconds (from `voiceover.json`)
- `data-track-index`: sequential track index per scene

Audio is wired via `<audio>` elements with matching `data-start`, `data-duration`, and `data-track-index` attributes. Animations use GSAP with a paused timeline for fade-in and slide-up effects. Visual Treatment parameters (colors, fonts, sizes) appear as inline CSS.

## Rules

- The composition is deterministic: same inputs always produce the same `index.html`.
- The composition requires an approved `SCRIPT.md`, existing `voiceover.json`, and existing `STORYBOARD.md` to generate.
- The `composition/` directory must not already exist when generating a new composition (no silent overwrites).
- Audio file paths in the HTML are relative to the composition directory so the run remains portable.
- The composition targets a 9:16 vertical video format (1080×1920).

## Scope Boundary

This artifact does **not** include HyperFrames catalog imports, B-roll assets, image generation, or web UI controls. It is a deterministic HTML representation generated from storyboard scenes with timing and treatment parameters.
