Status: completed

# Add Pipeline Progress event log

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Add **Pipeline Progress** event models, append-only Production Run persistence, and CLI progress formatting. Events must support both human-readable terminal output and JSONL output for automation.

## Acceptance criteria

- [ ] Progress events include phase, status, timestamp, message, artifact path, provider/model metadata when available, and error diagnostic when failed.
- [ ] Progress events can be appended to `.runs/<run-id>/progress.jsonl`.
- [ ] The append-only log can be read back for inspection.
- [ ] Text progress formatting is human-readable.
- [ ] JSONL progress formatting emits one valid JSON object per event.
- [ ] Tests cover serialization, append behavior, text output, and JSONL output.

## Blocked by

None - can start immediately
