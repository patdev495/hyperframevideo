Status: completed

# Add DeepSeek Script Drafting Provider

## Parent

.scratch/pipeline-orchestrator/PRD.md

## What to build

Implement DeepSeek as the first **Script Drafting Provider**. The provider should call DeepSeek's chat API, use the existing **Script Drafting Prompt**, return structured provider metadata, and read credentials from environment variables.

## Acceptance criteria

- [ ] Provider reads `DEEPSEEK_API_KEY`.
- [ ] Provider supports optional `DEEPSEEK_BASE_URL`.
- [ ] Provider supports optional `DEEPSEEK_MODEL` and CLI model override.
- [ ] Missing API key produces a readable diagnostic.
- [ ] Successful responses return script markdown and provider metadata.
- [ ] API errors produce readable provider errors.
- [ ] Tests mock HTTP responses and do not call the real network.

## Blocked by

- .scratch/pipeline-orchestrator/issues/02-add-script-drafting-provider-interface.md
