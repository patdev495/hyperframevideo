Status: completed

# Add Script Drafting Provider interface

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Add the provider-neutral **Script Drafting Provider** interface and result model for drafting and repairing **Source-Grounded Script** artifacts. Use a fake provider in tests to prove the orchestrator can call a provider without knowing the backing API.

## Acceptance criteria

- [ ] Provider interface supports `draft_script` from **Source Evidence** and **Script Drafting Prompt**.
- [ ] Provider interface supports bounded `repair_script` for malformed script output.
- [ ] Provider result includes script markdown, provider name, model, warnings, and raw usage when available.
- [ ] Providers are scoped to **Source-Grounded Script** only.
- [ ] Tests cover fake provider draft and repair behavior.

## Blocked by

None - can start immediately
