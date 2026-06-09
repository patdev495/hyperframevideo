Status: ready-for-agent

# Pipeline Orchestrator PRD

## Problem Statement

The current **News-to-Video Pipeline** works, but the user must run each CLI phase manually: create a **Production Run**, copy source evidence into a chatbot, paste back `SCRIPT.md`, approve the script, generate voiceover, generate storyboard, compose, and optionally render. This is slow, error-prone, and hard to track across failures or interruptions.

The user wants a higher-level CLI workflow that can run the pipeline from beginning to end, show progress in the terminal, persist progress inside the **Production Run**, and use DeepSeek API to draft or repair `SCRIPT.md`. The design must keep room for additional script APIs later and must not let LLM providers take over storyboard or HyperFrames composition work.

## Solution

Add a **Pipeline Orchestrator** command that coordinates the existing pipeline phases and records **Pipeline Progress**. The orchestrator will support both **Direct Source Request** and **Discovery Request** inputs, draft `SCRIPT.md` through a **Script Drafting Provider**, stop at **Script Approval** by default, and resume safely when rerun with the same `run-id`.

DeepSeek will be the first **Script Drafting Provider**. It will use environment variables for credentials and support a CLI model override. The provider can draft a **Source-Grounded Script** from `source-evidence.json`, and can perform one bounded **Script Repair** attempt if the draft does not match the expected artifact structure.

The orchestrator will support these defaults:

- Stop at `script_approval` unless `--auto-approve-script` is passed.
- Run through composition when script auto-approval is enabled.
- Render only when an explicit render flag is passed.
- Skip existing artifacts instead of overwriting them.
- Print progress in human-readable text by default.
- Support JSONL progress output for automation.
- Append all progress events to `.runs/<run-id>/progress.jsonl`.

## User Stories

1. As a pipeline user, I want one CLI command to start a video from a source URL, so that I do not have to remember every individual phase command.
2. As a pipeline user, I want the orchestrator to call DeepSeek to draft `SCRIPT.md`, so that I do not have to manually copy source evidence into a chatbot.
3. As a pipeline user, I want the CLI to stop at **Script Approval** by default, so that I can review factual accuracy before voiceover and render.
4. As a pipeline user, I want an `--auto-approve-script` option, so that trusted batch runs can continue without manual approval.
5. As a pipeline user, I want render to be opt-in, so that missing FFmpeg or slow rendering does not block earlier artifact generation.
6. As a pipeline user, I want progress shown in the terminal, so that I know which phase is running and what artifact was produced.
7. As a pipeline user, I want progress recorded in `progress.jsonl`, so that interrupted runs remain inspectable.
8. As a pipeline user, I want rerunning the same `run-id` to resume safely, so that completed artifacts are not overwritten.
9. As a pipeline user, I want failed phases to record readable diagnostics, so that I can fix credentials, script format, or missing runtime tools.
10. As a pipeline user, I want DeepSeek configuration to use environment variables, so that API keys are not stored in the repo.
11. As a pipeline user, I want a model override flag, so that I can switch DeepSeek models without code changes.
12. As a future implementer, I want a **Script Drafting Provider** interface, so that OpenAI, Anthropic, local models, or other APIs can be added later.
13. As a future implementer, I want provider metadata recorded, so that model, provider, warnings, and token/cost diagnostics can be inspected.
14. As a developer, I want **Script Repair** bounded to one retry in v1, so that bad LLM output does not create infinite loops.
15. As a developer, I want the provider restricted to **Source-Grounded Script**, so that storyboard and composition stay deterministic in this repo.
16. As a developer, I want tests around progress events, resume behavior, provider abstraction, and orchestrated CLI flow, so that future refactors do not break the high-level workflow.

## Implementation Decisions

- Add a top-level orchestrated CLI command shaped like `hyperframe-video run`.
- Support input through either `--url` or `--discover`, matching existing lower-level flows.
- Keep existing lower-level CLI commands available.
- Use **Pipeline Progress** events for both live CLI output and append-only `progress.jsonl`.
- Use phase names: `extract_source`, `draft_script`, `script_approval`, `voiceover`, `storyboard`, `compose`, `render`.
- Use progress statuses: `started`, `completed`, `failed`, `skipped`, `waiting_for_approval`.
- Default progress output is text; `--progress-format jsonl` emits JSONL progress events to stdout.
- Add **Pipeline Resume** behavior that skips artifacts already present in the run.
- Do not overwrite existing artifacts in v1.
- Use a **Script Drafting Provider** interface.
- Implement DeepSeek as the first provider.
- Configure DeepSeek with `DEEPSEEK_API_KEY`, optional `DEEPSEEK_BASE_URL`, optional `DEEPSEEK_MODEL`, and CLI model override.
- Keep the existing **Script Drafting Prompt** as the prompt basis for provider calls.
- Provider result should include script markdown, provider name, model, warnings, and raw usage when available.
- DeepSeek may perform one **Script Repair** attempt if the draft is malformed.
- The default orchestrated flow stops at **Script Approval** with `Status: draft`.
- `--auto-approve-script` allows the orchestrator to set `Status: approved` and continue.
- `--render` opts into render after composition.

## Testing Decisions

- Test behavior through public APIs and CLI entry points.
- Add unit tests for **Pipeline Progress** event serialization and append-only writing.
- Add tests for text and JSONL progress formatters.
- Add tests for **Script Drafting Provider** interface using a fake provider.
- Add DeepSeek adapter tests with mocked HTTP responses.
- Add orchestrator tests for default stop at **Script Approval**.
- Add orchestrator tests for `--auto-approve-script` continuing through voiceover/storyboard/compose with fake providers.
- Add orchestrator tests for `--render` opt-in.
- Add resume tests proving existing artifacts are skipped and not overwritten.
- Preserve all existing lower-level CLI tests.

## Out of Scope

- Web UI.
- Config files for provider credentials.
- Overwrite/redo flags.
- Concurrent batch orchestration.
- Cloud rendering.
- Non-script LLM providers for storyboard/composition.
- Multiple Script Repair retries beyond the v1 bounded retry.
- Implementing OpenAI, Anthropic, or local model providers in the first pass.

## Further Notes

This PRD extends the earlier manual **Script Drafting Prompt** workflow rather than replacing it. Users can still draft manually; the **Pipeline Orchestrator** adds an integrated path for users who want a single CLI flow with progress tracking.
