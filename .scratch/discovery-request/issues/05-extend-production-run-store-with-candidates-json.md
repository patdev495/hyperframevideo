Status: ready-for-agent

# Extend Production Run Store to write candidates.json

## Parent

`.scratch/discovery-request/PRD.md`

## What to build

Extend `ProductionRunStore` to support writing `candidates.json` into the **Production Run** directory. This artifact records the full list of `NewsCandidate` objects that were presented to the user, plus which one was selected (by URL or index).

The store should expose a new method (e.g. `write_candidates`) that accepts the candidates list and the selected candidate, serializes them to JSON, and writes `candidates.json` alongside the existing artifacts. The `Production Run` path layout already owns all artifact file naming — this is the only place that should know the filename `candidates.json`.

Runs created from a **Direct Source Request** do not write `candidates.json` — this file is only present when a **Discovery Request** was used.

## Acceptance criteria

- [ ] `ProductionRunStore` exposes a method to write `candidates.json` to the run directory.
- [ ] `candidates.json` contains the full list of candidates (url, title, source_name, published_at, summary) and identifies the selected candidate.
- [ ] Runs from **Direct Source Requests** do not produce `candidates.json`.
- [ ] Tests verify the file is written with the correct structure using a temporary run directory.
- [ ] The filename `candidates.json` is defined in one place only (the store), not hardcoded elsewhere.

## Blocked by

- `.scratch/discovery-request/issues/01-add-discovery-request-and-news-candidate-models.md`
