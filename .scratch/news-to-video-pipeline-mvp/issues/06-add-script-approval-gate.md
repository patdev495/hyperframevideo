Status: ready-for-agent

# Add Script Approval Gate

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Create the **Script Approval** gate that reads `SCRIPT.md` status and determines whether downstream work may continue. Future voiceover and render commands must be able to reuse this gate so they refuse to run unless the script is approved.

This slice does not need to implement TTS or rendering.

## Acceptance criteria

- [x] The gate can parse `Status: draft` from `SCRIPT.md`.
- [x] The gate can parse `Status: approved` from `SCRIPT.md`.
- [x] Missing status is treated as not approved.
- [x] Unknown status values are treated as not approved with a clear diagnostic.
- [x] The gate exposes a simple typed result for callers.
- [x] Tests cover draft, approved, missing status, unknown status, and case/spacing behavior if supported.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/05-generate-selected-story-and-draft-script.md`
