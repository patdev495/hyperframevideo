Status: ready-for-agent

# Build Source Evidence from extracted content

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Build the **Source Evidence** normalization layer that converts extracted source content into the project's evidence artifact shape. The output must be suitable for writing to `source-evidence.json` and for use by Codex, external chatbots, or future LLM integrations.

This slice should preserve source grounding and make missing or weak metadata visible through warnings.

## Acceptance criteria

- [ ] Extracted content is normalized into a typed Source Evidence model.
- [ ] Source Evidence includes URL, title, source name when available, publish date when available, extracted text, and warnings.
- [ ] Missing title, missing publish date, and low-content extraction produce warnings.
- [ ] Important source fields are serializable to JSON without ad hoc dictionary assembly at call sites.
- [ ] Tests cover complete metadata, missing metadata, and low-content extraction cases.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/02-create-production-run-store.md`
- `.scratch/news-to-video-pipeline-mvp/issues/03-extract-direct-source-content.md`
