Status: done

# Add DiscoveryRequest and NewsCandidate typed models

## Parent

`.scratch/discovery-request/PRD.md`

## What to build

Extend the typed model layer with two new dataclasses: `DiscoveryRequest` and `NewsCandidate`.

`DiscoveryRequest` captures a user's topic query and the requested number of candidates. It is the Discovery-mode parallel to the existing `DirectSourceRequest`.

`NewsCandidate` is the normalized output of a search result: URL, title, source name, optional publish date, and a one-line summary. It is the typed boundary object passed between the Discovery Engine, News Candidate Builder, Candidate Selector, and Production Run Store.

Both models must use the same frozen dataclass convention already established in `models.py`. No business logic belongs here — pure data shapes only.

## Acceptance criteria

- [ ] `DiscoveryRequest` dataclass exists with `query: str` and `candidate_count: int` fields.
- [ ] `DiscoveryRequest` has a sensible default for `candidate_count` (5).
- [ ] `NewsCandidate` dataclass exists with `url`, `title`, `source_name`, `published_at` (optional), and `summary` (optional) fields.
- [ ] Both models are frozen and use slots, consistent with the existing model convention.
- [ ] At least one unit test asserts the default `candidate_count` and that `NewsCandidate` accepts missing optional fields gracefully.

## Blocked by

None — can start immediately
