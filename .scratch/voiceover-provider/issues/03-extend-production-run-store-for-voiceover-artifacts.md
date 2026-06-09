Status: ready-for-agent

# Extend Production Run Store for voiceover artifacts

## Parent

`.scratch/voiceover-provider/PRD.md`

## What to build

Extend **Production Run Store** so it owns voiceover artifact paths and writes a `voiceover.json` manifest. The manifest records provider name, segment order, narration text, relative audio path, duration seconds, and warnings for each generated segment.

This slice should centralize all voiceover filenames and directories in the store so later CLI, provider, storyboard, and web UI code do not hardcode artifact paths.

## Acceptance criteria

- [ ] **Production Run Store** exposes a path for `voiceover.json`.
- [ ] **Production Run Store** exposes or creates a dedicated directory for voiceover audio files.
- [ ] A caller can write a voiceover manifest for a **Production Run**.
- [ ] The manifest includes provider name and one entry per voiceover segment.
- [ ] Audio paths in the manifest are relative to the **Production Run** directory.
- [ ] Tests verify manifest structure and path layout using a temporary run directory.

## Blocked by

- `.scratch/voiceover-provider/issues/02-extract-approved-script-narration-segments.md`
