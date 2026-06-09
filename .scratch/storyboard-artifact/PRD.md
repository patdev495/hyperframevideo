Status: ready-for-agent

# Storyboard Artifact PRD

## Problem Statement

The **News-to-Video Pipeline** can now produce approved narration audio and a `voiceover.json` timing manifest for a **Production Run**, but it still has no artifact that translates the approved script and narration timing into visual instructions. That leaves a gap between spoken audio and future HyperFrames composition generation.

Creators need an inspectable **Storyboard Artifact** that says what should appear on screen for each narration segment, when it should appear, and how it should follow the selected **Visual Treatment**. Developers need this artifact before render work so HyperFrames integration can consume stable visual instructions rather than re-parsing `SCRIPT.md` and `voiceover.json` directly.

## Solution

Add a CLI-driven **Storyboard Artifact** phase for existing **Production Runs**. A creator runs a storyboard command after **Script Approval** and voiceover generation. The command validates that `SCRIPT.md` is approved, reads `voiceover.json`, extracts segment-level visual intent from `SCRIPT.md`, aligns each script segment with its voiceover timing, and writes `STORYBOARD.md`.

The first implementation should be deterministic and local. It should produce useful markdown from the current script format without calling external LLMs, downloading assets, generating HyperFrames composition files, or rendering MP4.

## User Stories

1. As a creator, I want to run storyboard generation after voiceover, so that the **Production Run** can move from audio-only artifacts toward a visual plan.
2. As a creator, I want the storyboard step to refuse unapproved scripts, so that visual planning only uses content that passed **Script Approval**.
3. As a creator, I want a readable diagnostic when `SCRIPT.md` or `voiceover.json` is missing or malformed, so that I know what to fix.
4. As a creator, I want each narration segment to become a storyboard scene, so that the visual plan follows the spoken audio.
5. As a creator, I want each scene to include timing from `voiceover.json`, so that later rendering can align visuals with narration.
6. As a creator, I want each scene to include on-screen text and visual notes, so that the short video has a clear visual direction before composition generation.
7. As a creator, I want `STORYBOARD.md` to live inside the **Production Run**, so that the run remains portable and inspectable.
8. As a creator, I want re-running storyboard generation to behave predictably, so that stale visual plans are not silently overwritten.
9. As a developer, I want storyboard parsing isolated from file paths and HyperFrames, so that script-to-scene extraction is testable.
10. As a developer, I want `ProductionRunStore` to own the `STORYBOARD.md` path and writing behavior, so filenames are centralized.
11. As a developer, I want the storyboard generator to consume typed script scene inputs and typed voiceover timing, so future rendering code can depend on stable contracts.
12. As a developer, I want the storyboard phase to stop before HyperFrames composition generation, so that render integration can be implemented as a separate phase.

## Implementation Decisions

- The next phase is **Storyboard Artifact**, not HyperFrames render, because ADR `0010` and `docs/future-extensions.md` reserve storyboarding for this repo before composition generation.
- The CLI remains the primary interface.
- The command shape should be `hyperframe-video --storyboard <run-id>` or an equivalent CLI mode that targets an existing **Production Run**.
- The storyboard step reads an existing **Production Run** and writes `STORYBOARD.md`; it does not create a new run.
- The step must load `SCRIPT.md` and evaluate it through the existing **Script Approval Gate**.
- The step must load `voiceover.json` and require one timing entry per narration segment.
- The storyboard extractor treats each `## Segment N` block as the source for scene metadata.
- The first supported script fields are `Narration:`, `On-screen text:`, `Purpose:`, and `Facts used:`.
- Segment matching should use stable segment IDs when available and script order as the fallback.
- `STORYBOARD.md` should include a header, the source run ID, the **Visual Treatment**, total estimated duration, and one scene per voiceover segment.
- Each scene should include segment ID, order, start time, duration, audio path, narration text, on-screen text, purpose, facts used, and visual direction.
- The first implementation should compute start times by accumulating `duration_seconds` from `voiceover.json`.
- The default **Visual Treatment** remains `ai-modern` unless `SCRIPT.md` declares another value.
- Re-running storyboard generation should fail with a readable diagnostic if `STORYBOARD.md` already exists. Replacement can be added later behind an explicit flag.
- The storyboard phase must not modify `SCRIPT.md`, `voiceover.json`, voiceover audio, HyperFrames composition files, or rendered MP4 output.

## Testing Decisions

- Tests should verify public behavior and artifact contracts, not private parser internals.
- Storyboard extraction should be tested with script markdown fixtures containing multiple segments.
- Voiceover timing loading should be tested with fixture `voiceover.json` payloads.
- Alignment tests should verify readable diagnostics for missing timing entries, extra timing entries, and missing script fields.
- `ProductionRunStore` tests should verify the `STORYBOARD.md` path and write behavior.
- CLI integration tests should create a temporary **Production Run** with approved `SCRIPT.md` and `voiceover.json`, run the storyboard command, and verify `STORYBOARD.md`.
- Existing Direct Source, Discovery Request, and Voiceover Provider CLI flows should remain unaffected.
- Tests should not require VieNeu runtime, HyperFrames installation, internet access, real audio playback, image assets, or browser rendering.

## Out of Scope

- HyperFrames composition generation.
- MP4 rendering.
- Asset download, B-roll search, image generation, or stock media retrieval.
- LLM-based visual rewriting.
- Web UI for storyboard editing.
- Presenter avatar, lip sync, subtitles, captions rendering, or audio mixing.
- Automatic modification of `SCRIPT.md`.
- Replacing existing `STORYBOARD.md` without an explicit future overwrite mode.

## Further Notes

- `docs/future-extensions.md` already defines `STORYBOARD.md` as responsible for visual instructions and dependent on approved script plus voiceover timing.
- ADR `0002` keeps the MVP CLI and agent-first.
- ADR `0003` expects storyboard artifacts to live inside **Production Runs**.
- ADR `0004` favors local-first execution and HyperFrames rendering later.
- ADR `0005` says this repo should use HyperFrames as a dependency, not fork it.
- ADR `0010` says external chatbots produce only `SCRIPT.md`; storyboarding belongs inside this repo.
