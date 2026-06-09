Status: done

# HyperFrames Composition and Render PRD

## Problem Statement

The **News-to-Video Pipeline** can now produce a `STORYBOARD.md` with timed scenes for an approved script with voiceover audio, but it has no artifact that translates those visual instructions into a format HyperFrames can render. There is no CLI command to generate a video from a **Production Run**.

Creators need a way to go from `STORYBOARD.md` to a playable `.mp4` in one or two CLI commands. Developers need the composition artifact on disk before encoding so that rendering remains inspectable, resumable, and replaceable.

## Solution

Add two CLI-driven phases after the **Storyboard Artifact** phase:

1. **Composition Generation**: translates `STORYBOARD.md`, `voiceover.json`, and `voiceover/` audio into a **HyperFrames Composition** (`composition/index.html`) with data-timed scenes, audio tracks, and a GSAP timeline inside the **Production Run**.

2. **MP4 Render**: runs `npx hyperframes render` on the composition directory to produce `output.mp4` inside the **Production Run**.

Both phases are deterministic, local-first, and require no API keys. Composition generation uses project-owned HTML templates with configurable **Visual Treatment** parameters.

## User Stories

1. As a creator, I want to generate a **HyperFrames Composition** from a storyboard, so that I can inspect the timed visual plan before rendering.
2. As a creator, I want to switch between **Visual Treatments** via a config file, so that the video style changes without code edits.
3. As a creator, I want to render the composition to MP4 from the CLI, so that I get a playable short video.
4. As a creator, I want the composition and render commands to refuse incomplete inputs, so that I get a clear diagnostic instead of a broken render.
5. As a creator, I want re-running composition generation to fail if composition files already exist, so that stale visual plans are not silently overwritten.
6. As a developer, I want composition generation isolated from FFmpeg and headless Chrome, so that it is testable without HyperFrames runtime.
7. As a developer, I want visual treatment parameters loaded from a JSON config file, so that new treatments can be added without changing Python code.
8. As a developer, I want `ProductionRunStore` to own the composition and render output paths, so that filenames are centralized.
9. As a developer, I want the render command to verify that Node.js, FFmpeg, and `npx hyperframes` are available, so that failures produce actionable diagnostics.

## Implementation Decisions

### Phase Structure

- The next phase is **HyperFrames Composition Generation**, not render directly, because the composition artifact must be inspectable and testable before encoding.
- A separate **MP4 Render** phase calls the HyperFrames CLI as a subprocess, keeping rendering replaceable.
- Both phases target an existing **Production Run** and write artifacts inside it.

### Composition Format

- One single `index.html` per **Production Run** containing all storyboard scenes with `data-start`, `data-duration`, and `data-track-index` attributes.
- Audio tracks are wired per scene using `<audio>` elements with `data-track-index`, matching the voiceover timing from `voiceover.json`.
- Animations use GSAP (loaded from CDN) with a paused timeline constructed from scene data.
- The composition directory lives at `.runs/<run-id>/composition/`.

### Visual Treatment Mapping

- A `treatments.json` config file maps **Visual Treatment** names to HTML/CSS parameters: colors, fonts, text sizes, transition durations, and layout classes.
- The first version ships with one default treatment (`ai-modern`) in the config.
- Composition generation reads the treatment name from the storyboard header and loads parameters from `treatments.json`.

### Render Mechanism

- The CLI runs `npx hyperframes render` in the composition directory as a subprocess.
- Before rendering, the CLI checks that `node`, `ffmpeg`, and `npx` are on `PATH`.
- The output MP4 is written to `.runs/<run-id>/output.mp4`.

### Templates

- Composition HTML is generated from a project-owned Jinja2-like string template (not externalized to files initially).
- The template produces valid HTML that works with `npx hyperframes preview` and `npx hyperframes render`.

## Testing Decisions

- Composition generation tests should verify HTML output with expected `data-*` attributes from typed `StoryboardScene` fixtures.
- Tests should verify that `treatments.json` parameters appear in the generated CSS/HTML.
- Tests should verify diagnostics for missing storyboard, missing voiceover, and missing treatments.
- The render phase tests should verify Node.js/FFmpeg checks and subprocess invocation without running real HyperFrames.
- `ProductionRunStore` tests should verify the composition directory path and render output path.
- Tests must not require real HyperFrames installation, Chrome, FFmpeg, or GPU.
- Existing Direct Source, Discovery Request, Voiceover Provider, and Storyboard CLI flows must remain unaffected.

## Out of Scope

- B-roll search, image generation, or stock media retrieval.
- Multiple compositions per **Production Run** (e.g., one per social platform).
- Web UI for composition editing.
- Presenter avatar, lip sync, captions rendering, or audio mixing.
- Cloud or distributed rendering (AWS Lambda, etc.).
- Non-MP4 output formats.
- Modifying `SCRIPT.md`, `voiceover.json`, or `STORYBOARD.md`.
- Replacing existing `composition/` or `output.mp4` without explicit overwrite mode.

## Further Notes

- HyperFrames is used via `npx` (npm package), not a Python SDK. See [ADR 0005](/docs/adr/0005-use-hyperframes-as-dependency-not-fork.md).
- Node.js 22+ and FFmpeg are required for the render phase only. Composition generation has no external runtime dependencies.
- `docs/future-extensions.md` section 4 already defines the HyperFrames Render Boundary.
- This phase stops before any web UI, asset download, or presentational rendering features.
