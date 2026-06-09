Status: ready-for-agent

# Build Discovery Engine with DuckDuckGo backend

## Parent

`.scratch/discovery-request/PRD.md`

## What to build

Build the `DiscoveryEngine` module. It accepts a `DiscoveryRequest` and returns a list of raw search result dicts from DuckDuckGo News. This module is the only place in the codebase that knows about the DuckDuckGo backend. Its interface must be stable enough that swapping the backend later requires no changes outside this module.

Use the `duckduckgo-search` package (`duckduckgo_search` on PyPI) added via `uv add`. The engine calls `DDGS().news(query, max_results=candidate_count)` and returns the raw result list. Network errors must be caught and re-raised as a readable diagnostic.

The engine does not normalize results — that is the News Candidate Builder's job.

## Acceptance criteria

- [ ] `duckduckgo-search` is added to project dependencies via `uv add`.
- [ ] `DiscoveryEngine` accepts a `DiscoveryRequest` and returns a list of raw result dicts.
- [ ] The number of results respects `DiscoveryRequest.candidate_count`.
- [ ] Network errors surface as readable diagnostics rather than raw tracebacks.
- [ ] Tests use a mocked DuckDuckGo client (no real network calls); at least one test covers the correct count of results returned and one covers error handling.

## Blocked by

- `.scratch/discovery-request/issues/01-add-discovery-request-and-news-candidate-models.md`
