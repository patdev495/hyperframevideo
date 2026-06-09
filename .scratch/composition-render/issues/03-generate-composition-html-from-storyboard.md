Status: done

# Generate composition HTML from storyboard

## Parent

`.scratch/composition-render/PRD.md`

## What to build

Add a composition generator that takes typed `StoryboardScene` inputs, a `TreatmentConfig`, and a **Production Run** reference, then produces a `composition/index.html` file ready for HyperFrames rendering. The HTML must include data-timed scenes, per-scene audio tracks, and a GSAP animation timeline.

This slice should produce a valid HyperFrames HTML file with deterministic output. It should not call `npx hyperframes`, FFmpeg, or download any dependencies.

## Acceptance criteria

- [ ] Generated `index.html` contains a single `<div id="stage">` wrapping all scenes.
- [ ] Each scene is a `<div>` with `data-composition-id`, `data-start`, `data-duration`, and `data-track-index` matching voiceover timing.
- [ ] Each scene includes narration text and on-screen text in the HTML body.
- [ ] Audio is wired as `<audio>` elements with matching `data-track-index` and relative `src` paths to voiceover WAVs.
- [ ] A GSAP timeline is constructed with fade-in and slide-up animations per scene.
- [ ] Visual Treatment parameters (colors, fonts, sizes) appear in inline CSS.
- [ ] Output is deterministic for the same inputs.
- [ ] Missing storyboard scenes or missing treatment produce readable diagnostics.
- [ ] Tests verify HTML content with data attributes, audio paths, timing values, and treatment CSS from typed fixtures.

## Blocked by

- `.scratch/composition-render/issues/02-create-treatment-config-and-loader.md`
