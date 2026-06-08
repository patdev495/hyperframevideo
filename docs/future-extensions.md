# Future Extension Contracts

The News-to-Video Pipeline MVP starts with a Direct Source to Draft flow. This document records the architectural boundaries and contracts for features intentionally excluded from the first slice, ensuring future implementations do not violate the initial design principles.

## 1. Discovery Request Boundary

The MVP currently only supports **Direct Source Requests** (providing a specific URL). In the future, the pipeline will support **Discovery Requests**.

**Contract:**
- A Discovery Request will accept a topic, keyword, or query.
- The pipeline will perform web search or feed aggregation.
- The output of a Discovery Request will be a list of `News Candidates`.
- The user (or an automated policy) must explicitly select one `News Candidate` to proceed.
- Once selected, the flow rejoins the existing MVP pipeline, treating the selected candidate's URL exactly like a Direct Source Request. This keeps the core pipeline linear and decouples extraction from discovery.

## 2. Voiceover Provider Contract

The system currently stops at `SCRIPT.md` generation and approval. Future steps will require converting the approved script text into audio.

**Contract:**
- The pipeline will define a `VoiceoverProvider` interface.
- Implementations must accept text from `SCRIPT.md` (specifically the `Narration` blocks) and output audio file paths (e.g., `.wav` or `.mp3`) into the Production Run directory.
- The first implementation should target local TTS (e.g., HyperFrames local TTS plugins) to maintain the local-first execution ADR.
- The interface must be abstract enough to support external API providers later (such as Vietnamese TTS providers like FPT.AI, Viettel AI, or Zalo AI) without changing the core orchestration logic.

## 3. STORYBOARD.md Responsibility Boundary

Currently, the `SCRIPT.md` artifact captures the story, the narration, on-screen text, and fact-checking. It does **not** specify animation timings, layouts, or visual assets.

**Contract:**
- `STORYBOARD.md` (or a similar future artifact) will be strictly responsible for visual instructions: layout selections, timing offsets, transition types, B-roll asset paths, and avatar states.
- `STORYBOARD.md` will depend on an approved `SCRIPT.md` (and generated voiceover audio timings) as its input.
- `SCRIPT.md` must never dictate specific HyperFrames layout code. It only declares *what* the text says and *why*, while `STORYBOARD.md` dictates *how* it looks.

## 4. HyperFrames Render Boundary

The project uses HyperFrames for composition and rendering, but intentionally avoids becoming a fork of the HyperFrames upstream repository.

**Contract:**
- HyperFrames is treated purely as a dependency and rendering engine.
- The News-to-Video Pipeline will handle all orchestration (fetching, LLM interaction, TTS scheduling, and storyboard generation).
- To render a video, the pipeline will translate `STORYBOARD.md` and the Production Run assets into a valid HyperFrames input payload (e.g., composition configuration or temporary build files).
- The pipeline will then execute the HyperFrames CLI/engine locally to produce the final `.mp4`. Orchestration logic stays in this repo.

## 5. Web UI Stack

The MVP is strictly CLI-first to prove the core pipeline mechanics. Eventually, a Web UI will be built to manage Production Runs and review scripts visually.

**Contract:**
- Any future frontend code must use **TypeScript** (JavaScript is not allowed).
- The frontend framework must be **Vue**.
- Styling must use **Tailwind CSS**.
- The Web UI will act as a thin client over the existing Python core orchestration APIs (which will expose the Production Run Store and Pipeline commands), rather than rewriting the pipeline logic in JavaScript.
