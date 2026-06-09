Status: completed

# Add orchestrated run command to Script Approval

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Add `hyperframe-video run` for the default orchestrated flow from source input through DeepSeek-backed script drafting, stopping at **Script Approval**. The command should create or resume a **Production Run**, write artifacts, record **Pipeline Progress**, and leave `SCRIPT.md` in `Status: draft`.

## Acceptance criteria

- [ ] `hyperframe-video run --url <url> --script-provider deepseek` creates or resumes a run.
- [ ] The command writes source evidence and selected story artifacts.
- [ ] The command uses a **Script Drafting Provider** to write `SCRIPT.md`.
- [ ] The default flow stops with `script_approval` in `waiting_for_approval`.
- [ ] Progress is printed live and appended to `progress.jsonl`.
- [ ] Existing lower-level commands still work.
- [ ] Tests use fake extraction/provider dependencies where needed.

## Blocked by

- .scratch/pipeline-orchestrator/issues/01-add-pipeline-progress-event-log.md
- .scratch/pipeline-orchestrator/issues/02-add-script-drafting-provider-interface.md
