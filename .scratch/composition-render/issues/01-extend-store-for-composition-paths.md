Status: done

# Extend Production Run Store for composition paths

## Parent

`.scratch/composition-render/PRD.md`

## What to build

Extend **Production Run Store** so it owns the `composition/` directory path and render output path, and can write composition files inside a **Production Run**. This keeps composition filenames centralized before CLI wiring.

## Acceptance criteria

- [ ] **Production Run** exposes a `composition_dir` property returning `.runs/<run-id>/composition/`.
- [ ] **Production Run** exposes a `render_output_path` property returning `.runs/<run-id>/output.mp4`.
- [ ] **Production Run Store** can write the composition `index.html` inside the composition directory.
- [ ] Store writing does not modify `SCRIPT.md`, `voiceover.json`, voiceover audio, or `STORYBOARD.md`.
- [ ] Tests verify path layout and write behavior using a temporary run directory.

## Blocked by

- `.scratch/storyboard-artifact/issues/07-wire-storyboard-command-end-to-end.md`
