Status: ready-for-agent

# Generate storyboard markdown

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Add a deterministic storyboard markdown generator that turns typed planned scenes into `STORYBOARD.md` content. The output should be readable by a creator and structured enough for later HyperFrames composition generation.

This slice should generate markdown only. It should not call HyperFrames, download assets, render video, or use an LLM.

## Acceptance criteria

- [ ] Generated markdown starts with `# Storyboard`.
- [ ] The header records the Production Run ID, Visual Treatment, total duration, and source artifacts.
- [ ] Each scene records segment ID, order, start time, duration, audio path, narration, on-screen text, purpose, facts used, and visual direction.
- [ ] The generator uses `Visual Treatment` from `SCRIPT.md` when present and defaults to `ai-modern`.
- [ ] Output is deterministic for the same inputs.
- [ ] Tests verify the markdown content from typed planned scene fixtures.

## Blocked by

- `.scratch/storyboard-artifact/issues/05-extend-production-run-store-for-storyboard.md`
