Status: ready-for-agent

# News-to-Video Pipeline MVP PRD

## Problem Statement

The user wants a local-first way to turn news into short, engaging video artifacts without starting from a web application or manually rebuilding the same structure each time. The MVP needs to prove the earliest reliable path in the **News-to-Video Pipeline**: accept a **Direct Source Request**, extract the source, produce trustworthy **Source Evidence**, create a local **Production Run**, and prepare a draft **Source-Grounded Script** that can be reviewed through **Script Approval**.

The current repo has product language, local issue tracking, artifact specs, and architectural decisions, but no implementation yet.

## Solution

Build a CLI and agent-first MVP that accepts a specific news URL and creates a local **Production Run** under `.runs/<run-id>/`. The run will contain extracted **Source Evidence**, `SELECTED_STORY.md`, and a draft `SCRIPT.md` that follows the project's script artifact format.

The MVP will use fetch plus a readability parser for normal article pages and fallback to Playwright for JavaScript-heavy sources. It will not render video yet. Rendering, **Voiceover Provider** integration, `STORYBOARD.md`, **Discovery Request**, and web UI support are future extensions built on the same artifact model.

## User Stories

1. As a creator, I want to provide a specific news URL, so that the system can start from the source I already chose.
2. As a creator, I want each source to become a local **Production Run**, so that I can inspect, resume, or revise work later.
3. As a creator, I want source extraction to work for common article pages, so that I can avoid manually copying article text.
4. As a creator, I want extraction to fallback to browser rendering when needed, so that JavaScript-heavy news pages can still be processed.
5. As a creator, I want `source-evidence.json` to include the URL, title, source name, publish date when available, extracted text, and warnings, so that I can judge whether the source is usable.
6. As a creator, I want `SELECTED_STORY.md` to summarize the source and explain why it is the selected story, so that the production run has readable context.
7. As a creator, I want `SCRIPT.md` to start as `Status: draft`, so that no downstream voiceover or rendering step treats it as approved by accident.
8. As a creator, I want the draft script to use the **Curiosity-Driven News Explainer** tone, so that the video can be engaging without becoming misleading.
9. As a creator, I want the draft script to fit the **Duration Budget**, so that future voiceover and rendering steps do not produce videos longer than intended.
10. As a creator, I want each script segment to include narration, on-screen text, purpose, and facts used, so that later storyboard and HyperFrames composition work has enough structure.
11. As a creator, I want important factual claims to trace back to **Source Evidence**, so that the script remains source-grounded.
12. As a creator, I want the system to avoid copying long passages from a source article, so that the output is an original video script rather than a republished article.
13. As a creator, I want a portable **Script Drafting Prompt**, so that I can ask Codex, ChatGPT, Grok, or another chatbot to draft a compatible script.
14. As a creator, I want external chatbots to produce only `SCRIPT.md`, so that storyboard and HyperFrames implementation stay inside this repo.
15. As a creator, I want the script approval rule to be explicit, so that future TTS and render steps only run after I mark `SCRIPT.md` as approved.
16. As a developer, I want a deep **Production Run Store** module, so that artifact paths and file formats are centralized and testable.
17. As a developer, I want a deep **Source Extractor** module, so that fetch/readability extraction and Playwright fallback are isolated behind a stable interface.
18. As a developer, I want a **Source Evidence Builder**, so that raw extraction results are normalized before script drafting.
19. As a developer, I want a **Script Artifact Generator**, so that `SCRIPT.md` follows one contract regardless of whether Codex, an external chatbot, or a future LLM API writes the final script.
20. As a developer, I want future **Voiceover Provider** support to remain possible, so that the MVP can start with English local TTS later without blocking Vietnamese providers.
21. As a developer, I want HyperFrames to remain a dependency and rendering layer, so that this repo owns orchestration instead of becoming a fork of upstream HyperFrames.
22. As a developer, I want the MVP to stay CLI-first, so that the core pipeline can be proven before building a web UI.

## Implementation Decisions

- The MVP starts with **Direct Source Request** support only. **Discovery Request** support is out of scope for the first slice.
- The implementation is CLI and agent-first, not web app-first.
- The project runs local-first. Internet access may be used to read a current source URL, but orchestration and artifacts live on the user's machine.
- Each **Production Run** is stored under `.runs/<run-id>/`.
- A **Production Run** for this MVP must produce at least `source-evidence.json`, `SELECTED_STORY.md`, and `SCRIPT.md`.
- Source extraction uses fetch plus a readability parser first, then Playwright fallback when needed.
- External article extraction APIs are not part of the MVP.
- `SCRIPT.md` follows the structure documented in `docs/artifacts/script.md`.
- `SCRIPT.md` starts with `Status: draft`.
- **Script Approval** is represented by changing script status from `draft` to `approved`.
- Future TTS and render commands must refuse to run unless `SCRIPT.md` is approved.
- The default script language for the MVP is English.
- The default tone is **Curiosity-Driven News Explainer**.
- The default output assumption is **Vertical Short Video**, 9:16, using the default **Visual Treatment**.
- The default **Duration Budget** is 60-90 seconds, with a hard cap of 5 minutes.
- **Source-Grounded Script** drafting must avoid unsupported claims and long copied source passages.
- The project keeps `docs/prompts/script-drafting.md` as the portable **Script Drafting Prompt** for Codex, ChatGPT, Grok, and future LLM integrations.
- External chatbots should draft `SCRIPT.md` only. `STORYBOARD.md` and HyperFrames composition work remain inside this repo.
- HyperFrames is used as a dependency and rendering layer, not forked into this repo.
- **Voiceover Provider**, `STORYBOARD.md`, HyperFrames render, **Discovery Request**, and web UI support are planned extension areas but should not complicate the first slice.
- Python code must use `uv` for environment and dependency management.
- Python modules should use explicit typed data models for data crossing module boundaries rather than loose dictionaries.
- JavaScript code must be TypeScript.
- If a frontend is added later, it must use Vue and Tailwind CSS.

The major modules are:

- **CLI Orchestrator**: parses the Direct Source Request, creates the Production Run, and calls the other modules in order.
- **Production Run Store**: owns `.runs/<run-id>/` creation, artifact naming, and file writes.
- **Source Extractor**: extracts article content through readability-first extraction with Playwright fallback.
- **Source Evidence Builder**: normalizes extraction results into source evidence with warnings.
- **Script Artifact Generator**: writes a draft `SCRIPT.md` stub or draft structure using the artifact spec.
- **Script Drafting Prompt**: maintains portable prompt instructions for Codex and external chatbots.
- **Script Approval Gate**: parses `SCRIPT.md` status and blocks future downstream steps when status is not approved.
- **Future Extension Interfaces**: keep room for Voiceover Provider, storyboard, HyperFrames render, Discovery Request, and web UI without implementing them in the first slice.

## Testing Decisions

- Tests should focus on external behavior and artifact contracts, not private helper details.
- **Production Run Store** should be tested because it defines the artifact contract that future CLI, render, and web UI flows will depend on.
- **Source Extractor** should be tested with local HTML fixtures and controlled fallback behavior rather than live news sites.
- **Source Evidence Builder** should be tested for normalized fields, missing publish date warnings, missing title warnings, and URL preservation.
- **Script Artifact Generator** should be tested for required headers, `Status: draft`, segment structure, default language, default tone assumptions, target duration, visual treatment, and fact-check section.
- **Script Approval Gate** should be tested for `draft`, `approved`, missing status, and unknown status values.
- Do not test live HyperFrames render, TTS, or web search in this MVP slice because they are out of scope.
- Playwright fallback tests may use mocked or local browser-rendered fixtures to avoid depending on external websites.

## Out of Scope

- **Discovery Request** web search that returns 5-6 **News Candidates**.
- Multi-source aggregation for a selected event.
- Automatic app-owned LLM API script drafting.
- Vietnamese narration.
- Implementing external **Voiceover Provider** integrations.
- HyperFrames TTS, transcript timing, storyboard generation, composition generation, preview, validation, or MP4 render.
- Web UI.
- Presenter avatar.
- Multiple **Visual Treatment** presets beyond documenting the default direction.
- Forking or vendoring the HyperFrames upstream repo.
- External article extraction APIs.
- Fully offline operation without internet access.

## Further Notes

- The local machine currently has Node and npm available, but FFmpeg is not installed. FFmpeg will be required once render support is added.
- The MVP should keep file artifacts human-readable because Codex, external chatbots, and future app-owned LLM integrations will all rely on the same production-run structure.
- The first implementation issues should be vertical slices that produce demoable artifacts, starting with creating a Production Run from a Direct Source Request.
- The PRD is published to the local markdown issue tracker and should be broken into implementation issues with `to-issues` when ready.
