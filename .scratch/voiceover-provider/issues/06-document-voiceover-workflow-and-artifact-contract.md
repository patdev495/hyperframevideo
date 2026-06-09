Status: done

# Document Voiceover workflow and artifact contract

## Parent

`.scratch/voiceover-provider/PRD.md`

## What to build

Document how a creator moves from `SCRIPT.md` **Script Approval** to generated voiceover artifacts. The documentation should explain the CLI command, approval requirement, generated files, manifest fields, and how this phase prepares the **Production Run** for future `STORYBOARD.md` and HyperFrames render work.

This slice should keep the workflow CLI-first and should not promise production-quality speech from the first local provider.

## Acceptance criteria

- [x] Documentation explains that `SCRIPT.md` must be `Status: approved`.
- [x] Documentation shows the voiceover CLI command.
- [x] Documentation lists generated voiceover files and `voiceover.json`.
- [x] Documentation explains that `voiceover.json` is the timing and audio contract for future storyboard work.
- [x] Documentation states that VieNeu-TTS is the first real provider target and explains setup/runtime limitations.
- [x] Documentation does not introduce storyboard, HyperFrames composition, MP4 render, or web UI work into this phase.

## Blocked by

- `.scratch/voiceover-provider/issues/05-wire-voiceover-command-end-to-end.md`
