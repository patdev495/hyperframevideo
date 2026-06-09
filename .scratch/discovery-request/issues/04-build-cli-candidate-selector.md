Status: ready-for-agent

# Build CLI Candidate Selector

## Parent

`.scratch/discovery-request/PRD.md`

## What to build

Build the `CandidateSelector` module. It receives a list of `NewsCandidate` objects, prints a numbered menu to stdout, reads a selection from stdin, and returns the chosen `NewsCandidate`.

Menu format per candidate: index number, title, source name, publish date (or "unknown"), and summary (or "no summary"). After printing the menu, prompt the user to enter a number. On invalid input (non-integer or out-of-range), re-prompt without crashing. If the user enters `0` or `q`, return a sentinel value (`None` or a typed `RerunSignal`) so the CLI orchestrator knows to re-run the search.

This module must not know about the search backend or network — it operates purely on the typed `NewsCandidate` list it is given.

## Acceptance criteria

- [ ] `CandidateSelector.select(candidates)` prints a numbered menu to stdout.
- [ ] Menu shows index, title, source name, publish date, and summary for each candidate.
- [ ] Valid index input returns the corresponding `NewsCandidate`.
- [ ] Invalid input (non-integer, out-of-range) re-prompts without crashing.
- [ ] Input of `0` or `q` signals re-run (returns `None` or a typed sentinel).
- [ ] Tests inject fixture candidates and simulate stdin; cover valid selection, invalid input loop, and re-run signal — no real terminal required.

## Blocked by

- `.scratch/discovery-request/issues/01-add-discovery-request-and-news-candidate-models.md`
- `.scratch/discovery-request/issues/03-build-news-candidate-builder.md`
