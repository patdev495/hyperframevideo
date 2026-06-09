Status: done

# Create Production Run Store

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Create a **Production Run Store** that owns creation and file layout for `.runs/<run-id>/`. It should centralize artifact names and paths so later slices can write `source-evidence.json`, `SELECTED_STORY.md`, `SCRIPT.md`, and future artifacts without duplicating path logic.

The store should use typed models or value objects for run identifiers and artifact references where data crosses module boundaries.

## Acceptance criteria

- [x] A caller can create a new Production Run and receive its run identifier and artifact paths.
- [x] New Production Runs are created under `.runs/<run-id>/`.
- [x] The store exposes paths for `source-evidence.json`, `SELECTED_STORY.md`, and `SCRIPT.md`.
- [x] Run creation is deterministic enough to test without depending on wall-clock-only behavior.
- [x] Existing runs are not overwritten accidentally.
- [x] Tests cover run creation, artifact path generation, and duplicate/collision behavior.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/01-scaffold-python-cli-project-with-uv.md`
