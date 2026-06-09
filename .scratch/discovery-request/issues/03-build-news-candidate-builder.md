Status: ready-for-agent

# Build News Candidate Builder

## Parent

`.scratch/discovery-request/PRD.md`

## What to build

Build the `NewsCandidateBuilder` module. It accepts the raw result list from the `DiscoveryEngine` and normalizes each entry into a typed `NewsCandidate` object.

Field mapping from DuckDuckGo raw result: `url` → `url`, `title` → `title`, `source` → `source_name`, `date` → `published_at` (optional), `body` → `summary` (truncated to one sentence if long). Any field that is missing or empty in the raw result must degrade gracefully to `None`.

This module is the only place in the codebase that knows the shape of raw DuckDuckGo result dicts. If the backend changes in the future, only this module and the `DiscoveryEngine` need updating.

## Acceptance criteria

- [ ] `NewsCandidateBuilder.build(raw_results)` returns a list of typed `NewsCandidate` objects.
- [ ] All five fields are mapped correctly from the DuckDuckGo result shape.
- [ ] Missing or empty optional fields (`published_at`, `summary`) degrade to `None` without raising.
- [ ] `summary` is capped to a reasonable length (one sentence or ~150 characters) if the raw `body` is long.
- [ ] Tests use fixture raw result dicts (no network); at least one test covers full fields, one covers missing optional fields, and one covers summary truncation.

## Blocked by

- `.scratch/discovery-request/issues/01-add-discovery-request-and-news-candidate-models.md`
- `.scratch/discovery-request/issues/02-build-discovery-engine-with-duckduckgo-backend.md`
