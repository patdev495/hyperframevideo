Status: ready-for-agent

# Generate Selected Story and draft SCRIPT.md artifacts

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Generate the first human-readable artifacts for a **Production Run** after **Source Evidence** exists: `SELECTED_STORY.md` and draft `SCRIPT.md`. `SCRIPT.md` must follow `docs/artifacts/script.md`, start with `Status: draft`, and use the default MVP assumptions: English language, **Curiosity-Driven News Explainer** tone, 60-90 second **Duration Budget**, and `ai-modern` **Visual Treatment**.

This slice may generate a structured draft or stub that Codex or an external chatbot can refine, but it must preserve the required script sections and source-grounding shape.

## Acceptance criteria

- [x] `SELECTED_STORY.md` is generated from Source Evidence with readable story context.
- [x] `SCRIPT.md` is generated with `Status: draft`.
- [x] `SCRIPT.md` includes title, hook, Source-Grounded Script segments, fact check, and production notes sections.
- [x] Script segments include narration, on-screen text, purpose, and facts used.
- [x] The generated artifact references Source Evidence rather than unsupported claims.
- [x] The script artifact follows the structure documented in `docs/artifacts/script.md`.
- [x] Tests verify required headers, default values, required sections, and source-grounding placeholders.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/02-create-production-run-store.md`
- `.scratch/news-to-video-pipeline-mvp/issues/04-build-source-evidence.md`
