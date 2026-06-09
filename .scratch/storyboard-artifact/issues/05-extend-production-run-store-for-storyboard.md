Status: ready-for-agent

# Extend Production Run Store for storyboard

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Extend **Production Run Store** so it owns the `STORYBOARD.md` artifact path and writing behavior. This keeps storyboard filenames centralized before CLI wiring and later HyperFrames composition work.

## Acceptance criteria

- [ ] **Production Run Store** exposes a path for `STORYBOARD.md`.
- [ ] A caller can write storyboard markdown for a **Production Run**.
- [ ] Store writing does not modify `SCRIPT.md`, `voiceover.json`, or voiceover audio.
- [ ] Tests verify path layout and write behavior using a temporary run directory.

## Blocked by

- `.scratch/storyboard-artifact/issues/04-align-scenes-with-voiceover-timing.md`
