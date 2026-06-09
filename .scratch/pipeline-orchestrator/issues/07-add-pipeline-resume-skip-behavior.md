Status: completed

# Add Pipeline Resume skip behavior

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Implement **Pipeline Resume** for orchestrated runs. When a user reruns the same `run-id`, the orchestrator should skip already-created artifacts and continue from the next missing or gated phase without overwriting files.

## Acceptance criteria

- [ ] Existing `source-evidence.json` skips source extraction.
- [ ] Existing draft `SCRIPT.md` stops at **Script Approval**.
- [ ] Existing approved `SCRIPT.md` continues downstream.
- [ ] Existing `voiceover.json` skips voiceover.
- [ ] Existing `STORYBOARD.md` skips storyboard.
- [ ] Existing `composition/` skips compose.
- [ ] Existing `output.mp4` skips render.
- [ ] Each skip is recorded in `progress.jsonl`.
- [ ] Tests prove existing artifact contents are not overwritten.

## Blocked by

- .scratch/pipeline-orchestrator/issues/05-add-auto-approve-through-compose.md
- .scratch/pipeline-orchestrator/issues/06-add-optional-render-phase.md
