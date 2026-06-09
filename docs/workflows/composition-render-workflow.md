# Composition and Render Workflow

The **Composition** and **Render** phases are the final stages of the **News-to-Video Pipeline**. They turn an approved script with voiceover and storyboard into a playable MP4 video.

Both phases operate on an existing Production Run under `.runs/<run-id>/`.

## Prerequisites

Before running composition generation, the Production Run must have:

- `SCRIPT.md` with `Status: approved` in its header.
- `voiceover.json` written by the Voiceover Provider phase.
- `STORYBOARD.md` written by the Storyboard phase.
- For `premium-news`, `karaoke-captions.json` may already exist. If it does not,
  the compose command creates approximate **Karaoke Caption** timing from
  `voiceover.json`.

## 1. Generate Composition

Run the compose command with the Production Run ID:

```powershell
hyperframe-video --compose <run-id>
```

The command:

1. Reads and validates `SCRIPT.md`, `voiceover.json`, and `STORYBOARD.md`.
2. Loads the **Visual Treatment** from the `STORYBOARD.md` header (defaults to `premium-news` for new scripts).
3. Loads treatment parameters from the bundled `treatments.json` config.
4. Extracts script scenes and voiceover timing, then aligns them by segment ID.
5. For `premium-news`, reads or creates `karaoke-captions.json`.
6. Generates `composition/index.html` with data-timed scenes, audio tracks, and a GSAP animation timeline.
7. Copies voiceover WAV files to `composition/voiceover/`.
8. Fails with a readable diagnostic if `composition/` already exists, or if any prerequisite is missing.

On success, the Production Run contains:

```text
.runs/<run-id>/
|-- SCRIPT.md
|-- voiceover.json
|-- voiceover/
|-- STORYBOARD.md
|-- karaoke-captions.json    # premium-news only, approximate timing by default
`-- composition/
    |-- index.html
    `-- voiceover/
        |-- segment-001.wav
        `-- segment-002.wav
```

## 2. Render to MP4

Run the render command with the Production Run ID:

```powershell
hyperframe-video --render <run-id>
```

The command:

1. Verifies that `composition/` exists.
2. Checks that `output.mp4` does not already exist.
3. Checks system requirements: **Node.js 22+**, **FFmpeg**, and **npx** must be on `PATH`.
4. Runs `npx hyperframes render` in the composition directory.
5. Copies the generated `output.mp4` into the Production Run directory.

On success, the Production Run contains:

```text
.runs/<run-id>/
|-- ...
|-- composition/
|   |-- index.html
|   `-- voiceover/
`-- output.mp4
```

The command fails if system requirements are missing, the composition directory doesn't exist, or if `output.mp4` already exists.

## Visual Treatment Configuration

Visual Treatments are defined in `src/hyperframevideo/treatments.json`. Each treatment includes:

| Parameter | Default (`ai-modern`) | Description |
|-----------|----------------------|-------------|
| `background_color` | `#0f172a` | Background color |
| `text_color` | `#f8fafc` | Text color |
| `accent_color` | `#3b82f6` | Accent/highlight color |
| `font_family` | `Inter, sans-serif` | Font stack |
| `title_font_size` | `48px` | Narration text size |
| `body_font_size` | `24px` | Body text size |
| `fade_in_duration` | `0.5` | Fade-in animation duration (seconds) |
| `slide_up_duration` | `0.6` | Slide-up animation duration (seconds) |

To add a new treatment, add a new entry to the `treatments` array in `treatments.json` and reference it from the `STORYBOARD.md` header.

## Premium News and Karaoke Captions

The `premium-news` **Visual Treatment** uses deterministic HTML/CSS/GSAP
background layers, scene transitions, and **Karaoke Caption** overlays. The
caption overlay shows a short phrase window and highlights the active token
instead of showing the full narration body.

The first timing provider is approximate: it splits narration text into caption
tokens and distributes the segment duration from `voiceover.json` across those
tokens. This keeps the pipeline local-first and usable without GPU-heavy
alignment dependencies.

The caption timing contract is provider-neutral. A future Whisper-based provider
can write precise word timestamps into the same `karaoke-captions.json` artifact
without changing the **HyperFrames Composition** renderer. The installed
`vieneu 3.0.4` SDK currently exposes waveform generation and saving, but not a
public word timestamp API.

## Scope Boundary

This phase does **not** include B-roll search, image generation, asset downloads, presenter avatars, lip sync, precise Whisper alignment, audio mixing, cloud rendering, or web UI controls. It produces only the composition and rendered video from the existing Production Run artifacts.
