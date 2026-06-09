Status: completed

# Add auto-approve path through compose

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Extend the **Pipeline Orchestrator** so `--auto-approve-script` changes the drafted script to `Status: approved` and continues through voiceover, storyboard, and compose. The flow should still record progress and use existing artifact gates.

## Acceptance criteria

- [ ] `--auto-approve-script` approves the drafted script explicitly.
- [ ] The orchestrator runs voiceover, storyboard, and compose after approval.
- [ ] The orchestrator does not render unless render is explicitly requested.
- [ ] Progress records completed phases and artifact paths.
- [ ] Failures stop the pipeline and record a failed progress event.
- [ ] Tests use fake voiceover and provider dependencies to avoid external runtime work.

## Blocked by

- .scratch/pipeline-orchestrator/issues/04-add-orchestrated-run-command-to-script-approval.md
