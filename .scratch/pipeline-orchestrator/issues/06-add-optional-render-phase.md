Status: completed

# Add optional render phase

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Add explicit render opt-in to the **Pipeline Orchestrator**. Rendering should only run when the user passes the render flag, and should use the existing render behavior and system requirement checks.

## Acceptance criteria

- [ ] Orchestrated runs do not render by default.
- [ ] Passing the render flag runs the render phase after compose.
- [ ] Missing Node.js, npx, or FFmpeg records a failed progress event with a readable diagnostic.
- [ ] Successful render records `output.mp4` as an artifact path.
- [ ] Tests mock subprocess and tool detection.

## Blocked by

- .scratch/pipeline-orchestrator/issues/05-add-auto-approve-through-compose.md
