Status: ready-for-agent

# Extract Direct Source content with Readability-first fallback path

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Implement the **Source Extractor** for a **Direct Source Request**. It should first attempt lightweight article extraction using fetch plus a readability parser. It should also define and implement a Playwright fallback path for sources that require browser rendering.

This slice should focus on returning typed extracted source content. It should not write Production Run artifacts or draft scripts.

## Acceptance criteria

- [ ] A caller can pass a source URL and receive typed extracted content.
- [ ] The extractor preserves the original URL.
- [ ] The extractor captures title, extracted text, and any available publish date or source metadata.
- [ ] Readability-first extraction is attempted before Playwright fallback.
- [ ] Playwright fallback can be triggered in a controlled test scenario.
- [ ] Tests use local fixtures or mocked responses rather than live news sites.
- [ ] Extraction failures return actionable typed errors or warnings.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/01-scaffold-python-cli-project-with-uv.md`
