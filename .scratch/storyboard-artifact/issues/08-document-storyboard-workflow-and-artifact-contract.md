Status: done

# Document storyboard workflow and artifact contract

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Document how a creator moves from approved script and generated voiceover artifacts to `STORYBOARD.md`. The documentation should explain the CLI command, input requirements, generated file, scene fields, timing contract, and how this phase prepares the **Production Run** for future HyperFrames composition generation.

This slice should keep the workflow CLI-first and should not promise HyperFrames composition, MP4 render, or web UI work.

## Acceptance criteria

- [ ] Documentation explains that `SCRIPT.md` must be `Status: approved`.
- [ ] Documentation explains that `voiceover.json` must exist before storyboard generation.
- [ ] Documentation shows the storyboard CLI command.
- [ ] Documentation lists the generated `STORYBOARD.md` file.
- [ ] Documentation explains that `STORYBOARD.md` is the visual instruction contract for future HyperFrames composition generation.
- [ ] Documentation states that this phase does not generate HyperFrames composition files, MP4 output, assets, or web UI controls.

## Blocked by

- `.scratch/storyboard-artifact/issues/07-wire-storyboard-command-end-to-end.md`
