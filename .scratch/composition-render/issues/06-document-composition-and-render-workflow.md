Status: done

# Document composition and render workflow

## Parent

`.scratch/composition-render/PRD.md`

## What to build

Document how a creator moves from an approved script with voiceover and storyboard to a rendered MP4 video. The documentation should explain the two CLI commands (`--compose` and `--render`), input requirements, generated files, the `treatments.json` config, the Visual Treatment system, HyperFrames system requirements, and how this phase completes the **News-to-Video Pipeline**.

## Acceptance criteria

- [ ] Documentation explains that `STORYBOARD.md` and `voiceover.json` must exist before composition generation.
- [ ] Documentation shows the `--compose` CLI command.
- [ ] Documentation shows the `--render` CLI command.
- [ ] Documentation lists the generated `composition/index.html` and `output.mp4` files.
- [ ] Documentation explains the Visual Treatment config (`treatments.json`) and how to customize it.
- [ ] Documentation states that Node.js 22+ and FFmpeg are required for the render phase.
- [ ] Documentation explains that `output.mp4` is the final deliverable of the **News-to-Video Pipeline**.
- [ ] Documentation states that this phase does not include B-roll, image generation, or web UI.
- [ ] A documentation test verifies key content in both workflow and artifact docs.

## Blocked by

- `.scratch/composition-render/issues/05-wire-render-cli-command.md`
