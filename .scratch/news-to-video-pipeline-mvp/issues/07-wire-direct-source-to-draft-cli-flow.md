Status: ready-for-agent

# Wire Direct Source to Draft CLI flow

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Wire the implemented modules into a demoable CLI flow for the first MVP slice. A user should be able to provide a news URL as a **Direct Source Request** and receive a completed **Production Run** containing `source-evidence.json`, `SELECTED_STORY.md`, and draft `SCRIPT.md`.

This is the first end-to-end tracer bullet for the **News-to-Video Pipeline**. It should not implement **Discovery Request**, TTS, HyperFrames render, or web UI.

## Acceptance criteria

- [ ] A CLI command accepts a source URL.
- [ ] Running the command creates a new `.runs/<run-id>/` directory.
- [ ] The run contains `source-evidence.json`.
- [ ] The run contains `SELECTED_STORY.md`.
- [ ] The run contains `SCRIPT.md` with `Status: draft`.
- [ ] CLI output prints the created run path and next-step guidance for Script Approval.
- [ ] Failures produce readable diagnostics and do not leave misleading approved artifacts.
- [ ] An integration-style test covers the end-to-end flow using a local fixture source.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/02-create-production-run-store.md`
- `.scratch/news-to-video-pipeline-mvp/issues/03-extract-direct-source-content.md`
- `.scratch/news-to-video-pipeline-mvp/issues/04-build-source-evidence.md`
- `.scratch/news-to-video-pipeline-mvp/issues/05-generate-selected-story-and-draft-script.md`
