Status: done

# Wire Discovery Request into CLI Orchestrator

## Parent

`.scratch/discovery-request/PRD.md`

## What to build

Wire the Discovery Request flow into the existing CLI Orchestrator. This is the integration slice that connects all prior modules into a demoable end-to-end flow.

Add a `--discover "<query>"` flag to the CLI. When used, the orchestrator:
1. Builds a `DiscoveryRequest` from the query and optional `--candidates N` count (default 5).
2. Calls `DiscoveryEngine` to fetch raw results.
3. Calls `NewsCandidateBuilder` to normalize into `NewsCandidate` objects.
4. Calls `CandidateSelector` to present the menu and get the user's choice. If the user signals re-run (`0`/`q`), repeat from step 2.
5. Creates a `Production Run` via `ProductionRunStore`.
6. Writes `candidates.json` via the store's new method.
7. Turns the selected candidate's URL into a `DirectSourceRequest` and hands off to the existing `SourceExtractor` → `SourceEvidenceBuilder` → `StoryArtifactGenerator` chain unchanged.
8. Prints the run path and next-step guidance identical to the Direct Source flow.

The existing `url` positional argument and Direct Source behavior must remain completely unaffected.

## Acceptance criteria

- [x] `--discover "<query>"` flag is added to the CLI.
- [x] `--candidates N` flag controls candidate count (default 5).
- [x] Running `--discover` triggers the full Discovery flow end-to-end.
- [x] Re-run (`0`/`q`) loops the search without crashing.
- [x] The resulting **Production Run** directory contains `candidates.json`, `source-evidence.json`, `SELECTED_STORY.md`, and `SCRIPT.md`.
- [x] CLI output prints the created run path and the same next-step guidance as the Direct Source flow.
- [x] Existing Direct Source flow (positional URL argument) is unaffected.
- [x] An integration-style test covers the end-to-end Discovery flow using mocked search results and a fixture source page.
- [x] Failures at any stage produce readable diagnostics and do not leave misleading artifacts.

## Blocked by

- `.scratch/discovery-request/issues/02-build-discovery-engine-with-duckduckgo-backend.md`
- `.scratch/discovery-request/issues/03-build-news-candidate-builder.md`
- `.scratch/discovery-request/issues/04-build-cli-candidate-selector.md`
- `.scratch/discovery-request/issues/05-extend-production-run-store-with-candidates-json.md`
