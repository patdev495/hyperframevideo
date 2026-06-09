Status: ready-for-agent

# Voiceover Provider PRD

## Problem Statement

The **News-to-Video Pipeline** currently stops after creating a draft `SCRIPT.md` and asking the creator to perform **Script Approval** manually. That proves source reading, **Source Evidence**, **Selected Story**, and **Source-Grounded Script** drafting, but it does not yet move the **Production Run** toward a real **Vertical Short Video**. The next useful artifact is spoken narration audio.

Creators need a local-first way to turn an approved script's `Narration:` lines into voiceover artifacts that future storyboard and HyperFrames render work can consume. The system must refuse to generate audio from draft or malformed scripts, because downstream audio timing should only be based on approved content.

## Solution

Add a CLI-driven **Voiceover Provider** phase for existing **Production Runs**. A creator runs a voiceover command against a run ID after editing `SCRIPT.md` from `Status: draft` to `Status: approved`. The command validates **Script Approval**, extracts ordered narration segments from `SCRIPT.md`, sends them through a thin **Voiceover Provider** interface, writes audio files under the **Production Run**, and records a machine-readable `voiceover.json` manifest.

The first implementation should be local-first and deterministic enough for automated tests. It should establish the provider interface and artifact contract, then integrate VieNeu-TTS as the first real Vietnamese **Voiceover Provider** through a thin adapter. Automated tests should not run real model inference; they should use a fake SDK/provider while preserving the VieNeu-facing contract.

## User Stories

1. As a creator, I want to run voiceover generation after **Script Approval**, so that my **Production Run** can move beyond a text-only script.
2. As a creator, I want the voiceover step to refuse `Status: draft`, so that I do not accidentally generate audio from unfinished narration.
3. As a creator, I want a readable diagnostic when `SCRIPT.md` is missing, draft, or malformed, so that I know what to fix.
4. As a creator, I want every `Narration:` line in `SCRIPT.md` to become an ordered voiceover segment, so that spoken audio follows the approved script structure.
5. As a creator, I want generated voiceover audio files to live inside the **Production Run**, so that the run remains portable and inspectable.
6. As a creator, I want a `voiceover.json` manifest, so that I can see which script segment produced each audio file.
7. As a creator, I want the manifest to include segment order, narration text, audio path, duration, and provider name, so that future storyboard work can align visuals with audio.
8. As a creator, I want re-running voiceover generation to behave predictably, so that stale audio is not silently mixed with current script text.
9. As a creator, I want the first implementation to use a Vietnamese-focused local provider, so that narration quality matches the **Vertical Short Video** target better than English-only TTS.
10. As a creator, I want the first implementation to work locally without API keys after setup, so that I can keep iterating on the pipeline on my machine.
11. As a creator, I want room for other providers later, so that this first slice does not lock the project into one voice engine.
12. As a developer, I want a thin **Voiceover Provider** interface, so that VieNeu-TTS, HyperFrames local TTS, external APIs, and manual audio providers can be swapped without rewriting orchestration.
13. As a developer, I want narration extraction isolated from provider execution, so that script parsing is testable without audio generation.
14. As a developer, I want **Production Run Store** to own voiceover artifact paths, so that filenames are not hardcoded across the codebase.
15. As a developer, I want voiceover generation to depend on **Script Approval Gate**, so that the approval rule is enforced consistently.
16. As a developer, I want tests to avoid real network, model downloads, and heavyweight TTS inference, so that the voiceover phase remains safe for AFK implementation.
17. As a developer, I want the manifest schema to be stable enough for `STORYBOARD.md` generation, so that the next phase can consume voiceover timing directly.

## Implementation Decisions

- The next project phase is **Voiceover Provider**, not storyboard or render, because `STORYBOARD.md` depends on approved script content and voiceover timing.
- The CLI remains the primary user interface.
- The command shape should be `hyperframe-video voiceover <run-id>` or an equivalent CLI mode that clearly targets an existing **Production Run**.
- The voiceover step reads an existing **Production Run** rather than creating a new run.
- The step must load `SCRIPT.md` from the run directory and evaluate it through the existing **Script Approval Gate**.
- If the script is not approved, the command exits non-zero with a readable diagnostic and writes no voiceover artifacts.
- Narration extraction treats each `Narration:` line as one ordered voiceover segment.
- Segment identifiers should be stable and simple, such as `segment-001`, `segment-002`, based on script order.
- The **Voiceover Provider** interface accepts typed narration segments and writes or returns typed voiceover outputs.
- The first real local provider is VieNeu-TTS via the `vieneu` Python SDK.
- VieNeu-TTS is selected because current public package metadata describes it as on-device Vietnamese TTS with Apache-2.0 licensing, Python 3.10-3.13 support, built-in voices, CPU/GPU support, and a minimal CPU path that runs through ONNX rather than requiring PyTorch.
- The implementation should add VieNeu as an optional or isolated runtime dependency if feasible, because model downloads and native runtime dependencies should not slow ordinary tests or direct-source/discovery workflows.
- The VieNeu adapter should support a preset voice configuration first. Voice cloning from reference audio is deferred.
- A deterministic fake provider or fake VieNeu SDK should be used in automated tests instead of real inference.
- HyperFrames local TTS and external Vietnamese providers remain future provider implementations behind the same interface.
- Voiceover artifacts live inside the **Production Run**, preferably in a dedicated voiceover directory plus a top-level `voiceover.json` manifest.
- `voiceover.json` records provider name, generated timestamp if needed, segment order, narration text, relative audio path, duration seconds, and warnings.
- **Production Run Store** owns artifact paths and manifest writing.
- Re-running voiceover should either replace the previous manifest and owned audio directory or fail with a clear diagnostic. The first implementation should choose one predictable behavior and test it.
- The voiceover phase must not generate `STORYBOARD.md`, HyperFrames compositions, or MP4 output.
- The voiceover phase must not modify `SCRIPT.md`.

## Testing Decisions

- Tests should verify public behavior and artifact contracts, not private parser internals.
- **Script Narration Extractor** should be tested with approved script fixtures containing multiple `Narration:` lines and scripts with no narration.
- **Voiceover Provider** should be tested through a fake VieNeu SDK/provider, not live model inference.
- **Production Run Store** should be tested for voiceover paths and manifest structure.
- CLI integration tests should create a temporary **Production Run** with `SCRIPT.md`, run the voiceover command, and verify `voiceover.json` plus audio files.
- CLI failure tests should verify draft scripts fail without writing voiceover artifacts.
- Existing Direct Source and Discovery Request flows should remain unaffected.
- Tests should not depend on real VieNeu model downloads, real HyperFrames installation, internet access, microphone devices, OS speech settings, GPU availability, or paid TTS providers.

## Out of Scope

- `STORYBOARD.md` generation.
- HyperFrames composition generation.
- MP4 rendering.
- Automatic script drafting or script rewriting.
- Web UI controls for voice selection.
- Multi-language voice selection beyond preserving language metadata.
- Voice cloning from reference audio.
- External API providers such as OpenAI, ElevenLabs, FPT.AI, Zalo AI, or Viettel AI.
- Fine-grained speech prosody controls, pronunciation dictionaries, music, sound effects, or audio mixing.
- Subtitle generation from forced alignment.
- Presenter avatar or lip sync.

## Further Notes

- ADR `0001` now identifies VieNeu-TTS as the first real provider target while preserving the thin **Voiceover Provider** interface.
- ADR `0003` expects voiceover artifacts to live inside **Production Runs**.
- ADR `0004` favors local-first execution, so the first provider should be usable without network access.
- `docs/artifacts/script.md` already defines `Narration:` as the spoken voiceover text.
- This PRD intentionally creates the artifact and interface foundation needed before storyboard and render work.
