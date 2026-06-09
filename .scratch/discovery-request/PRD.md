Status: ready-for-agent

# Discovery Request PRD

## Problem Statement

The MVP **News-to-Video Pipeline** only accepts a **Direct Source Request** — the user must already know which URL they want to produce a video from. When the user wants to explore current news by topic or keyword and pick the best story, they have no supported workflow. They must leave the pipeline, manually search for news, evaluate articles themselves, and then re-enter the pipeline with a chosen URL. This breaks the creative flow and defeats the purpose of a local-first pipeline.

## Solution

Add a **Discovery Request** mode to the CLI. The user provides a topic, keyword, or query instead of a URL. The pipeline performs web search, evaluates each result as a **News Candidate** (with lightweight **Source Evidence**), and presents a numbered CLI menu for the user to select one. Once selected, the chosen candidate's URL is passed directly into the existing **Direct Source Request** pipeline — no duplication of extraction, evidence, or script logic.

The default search backend is DuckDuckGo News (no API key required, local-first). The number of candidates is configurable. Selection is performed interactively through a CLI prompt.

## User Stories

1. As a creator, I want to type a topic or keyword instead of a URL, so that the system can find current news for me.
2. As a creator, I want to see a numbered list of **News Candidates** after searching, so that I can quickly evaluate which story to produce.
3. As a creator, I want each **News Candidate** to show its title, source name, publish date, and a one-line summary, so that I can make an informed selection without opening each article.
4. As a creator, I want to enter a number to select a candidate, so that selection is fast and requires no extra tools.
5. As a creator, I want to be able to re-run the search if none of the candidates look suitable, so that I am not forced to accept a bad batch.
6. As a creator, I want the selected candidate to flow through the existing pipeline (extraction → evidence → story → script), so that the output is identical in structure to a **Direct Source Request**.
7. As a creator, I want the number of candidates shown to be configurable, so that I can request more results when topics are broad or fewer when I already have a good idea.
8. As a creator, I want the CLI to tell me when a search returns no results, so that I know to try a different query.
9. As a creator, I want the search to work without requiring an API key or paid subscription, so that I can run the pipeline locally without external accounts.
10. As a creator, I want the **Production Run** created from a **Discovery Request** to look identical to one created from a **Direct Source Request**, so that downstream steps (script approval, future TTS, future render) are unaffected.
11. As a developer, I want the **Discovery Engine** to be a deep module with a stable interface, so that the search backend can be swapped later without touching CLI or pipeline logic.
12. As a developer, I want the **News Candidate Builder** to be a deep module, so that raw search results are normalized into a typed **News Candidate** model before reaching the UI layer.
13. As a developer, I want the **Candidate Selector** to be isolated from the search backend, so that it can be tested with fixture candidates without making real network requests.
14. As a developer, I want a `DiscoveryRequest` typed model parallel to `DirectSourceRequest`, so that the CLI orchestrator dispatches cleanly between the two modes.
15. As a developer, I want the candidate list to be saved to `candidates.json` in the **Production Run** directory, so that the selection is traceable and reproducible.
16. As a developer, I want the `candidates` count to default to 5 and be overridable via a CLI flag, so that the behavior is predictable but flexible.

## Implementation Decisions

- A `DiscoveryRequest` typed dataclass is added to `models.py`, parallel to `DirectSourceRequest`. It holds the query string and the requested candidate count.
- The **Discovery Engine** accepts a `DiscoveryRequest` and returns a list of `NewsCandidate` typed objects. It is the only module that knows about DuckDuckGo or any future search backend. The interface is stable — returning a list of candidates — regardless of which backend is in use.
- The default backend is DuckDuckGo News via the `duckduckgo-search` Python package (zero API key, MIT licensed, local-first compliant with ADR `0004`).
- The **News Candidate Builder** normalizes raw search result dicts into typed `NewsCandidate` objects: `url`, `title`, `source_name`, `published_at` (optional), `summary` (one sentence extracted from snippet). It is the only module that knows the shape of raw DuckDuckGo results.
- The **Candidate Selector** receives a list of `NewsCandidate` objects, prints a numbered menu to stdout, reads a number from stdin, and returns the selected `NewsCandidate`. It has no knowledge of the search backend. If the user enters an invalid number, it re-prompts. If the user enters `0` or `q`, it signals that the search should be re-run.
- The **CLI Orchestrator** gains a `--discover` flag (or a `discover` subcommand). When `--discover <query>` is passed, it uses the Discovery flow; when a URL is passed, it uses the existing Direct Source flow. Both paths converge at `SourceExtractor` — the selected candidate's URL is turned into a `DirectSourceRequest` before extraction begins.
- The `ProductionRunStore` is extended to write `candidates.json` alongside the other artifacts, recording the full candidate list and which one was selected. This is the only store change needed.
- The candidate count defaults to `5` and is configurable via `--candidates N` CLI flag.
- The CLI prints a clean numbered menu: index, title, source name, publish date, and summary. No colors required for MVP of this feature.
- Re-run is triggered by entering `0` at the selection prompt, which re-calls the Discovery Engine with the same query.
- All network calls (DuckDuckGo search and source extraction) should surface errors as readable diagnostics, consistent with the existing error handling pattern in the CLI.

## Testing Decisions

- Tests should cover external behavior and typed contracts only — not internal DuckDuckGo client details.
- The **Discovery Engine** should be tested with a mocked `duckduckgo-search` client that returns fixture result dicts, verifying that the correct number of candidates is returned and that network errors are surfaced cleanly.
- The **News Candidate Builder** should be tested with fixture raw result dicts, verifying all fields are normalized correctly, optional fields (`published_at`, `summary`) degrade gracefully when absent, and the output is a valid typed `NewsCandidate`.
- The **Candidate Selector** should be tested by injecting fixture `NewsCandidate` lists and simulated stdin input, verifying correct candidate is returned for valid input, re-prompt occurs on invalid input, and `0`/`q` signals re-run correctly.
- The `ProductionRunStore` extension should be tested to verify `candidates.json` is written with the correct structure and that the selected candidate's URL is recorded.
- End-to-end integration test: use a fixture candidate list (bypassing real search), simulate selection via stdin, verify the resulting `Production Run` directory contains `candidates.json`, `source-evidence.json`, `SELECTED_STORY.md`, and `SCRIPT.md`.
- Do not make real DuckDuckGo network requests in tests. Use mocks or pre-recorded fixture responses.
- Prior art: follow the same fixture-and-mock pattern used in the existing `SourceExtractor` tests.

## Out of Scope

- Multi-source aggregation (combining multiple candidates into one script).
- Automatic candidate selection without user input.
- Filtering candidates by language, region, or publication date range.
- RSS feed aggregation as a search backend (may come later).
- Paid search API backends (SerpAPI, Google Custom Search, Brave Search).
- Saving search history or previously rejected candidates.
- Web UI for candidate selection.
- Vietnamese-language search queries (the pipeline searches in English by default; Vietnamese support is a future concern tied to the Voiceover Provider phase).

## Further Notes

- DuckDuckGo's news search does not require an API key and has no rate limits for light usage, making it the most local-first compatible backend available.
- The `duckduckgo-search` package (`duckduckgo_search` on PyPI) provides a clean Python interface. It should be added to project dependencies via `uv add`.
- The **Discovery Request** flow is intentionally designed to converge with the **Direct Source Request** flow at the `SourceExtractor` boundary. This means all future phases (Voiceover, Storyboard, Render) require zero changes to support discovery-originated runs.
- The `candidates.json` artifact preserves the full candidate list so future tooling (or the user) can inspect which stories were considered and which was chosen.
