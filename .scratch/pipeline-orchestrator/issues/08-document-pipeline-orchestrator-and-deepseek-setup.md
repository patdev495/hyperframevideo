Status: completed

# Document Pipeline Orchestrator and DeepSeek setup

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Document the orchestrated CLI workflow, DeepSeek environment variables, progress tracking, approval gate behavior, render opt-in, and safe resume behavior.

## Acceptance criteria

- [ ] Docs show default run-to-approval command.
- [ ] Docs show `--auto-approve-script`.
- [ ] Docs show render opt-in.
- [ ] Docs document `DEEPSEEK_API_KEY`, optional `DEEPSEEK_BASE_URL`, optional `DEEPSEEK_MODEL`, and model override.
- [ ] Docs explain `progress.jsonl` and `--progress-format jsonl`.
- [ ] Docs explain safe resume and no-overwrite behavior.
- [ ] Docs state providers may only draft or repair **Source-Grounded Script**.

## Blocked by

- .scratch/pipeline-orchestrator/issues/01-add-pipeline-progress-event-log.md
- .scratch/pipeline-orchestrator/issues/03-add-deepseek-script-drafting-provider.md
- .scratch/pipeline-orchestrator/issues/07-add-pipeline-resume-skip-behavior.md
