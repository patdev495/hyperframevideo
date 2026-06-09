# Hyperframe Video

This context describes the domain language for a system that turns current news into short Vietnamese narrated videos rendered with HyperFrames.

## Language

**News-to-Video Pipeline**:
A workflow that turns a news search request into a selected-news short video with Vietnamese narration and animated text.
_Avoid_: Video generator, news bot, automation

**News Candidate**:
A news item discovered from online sources and presented to the user as a possible video topic.
_Avoid_: Article, source, result

**Selected Story**:
The news item chosen by the user as the basis for the script, narration, and video.
_Avoid_: Chosen article, selected news, topic

**Source Evidence**:
The citation data and summary facts that prove a News Candidate is grounded in identifiable news sources.
_Avoid_: Reference, citation, metadata

**Direct Source Request**:
A request where the user provides a specific news URL or source item that should be read and used directly for video production.
_Avoid_: URL prompt, fixed source, article input

**Discovery Request**:
A request where the user asks the system to find possible video ideas from current news.
_Avoid_: Search prompt, idea search, news lookup

**Script Approval**:
The checkpoint where the user confirms the drafted video script before voiceover generation and rendering.
_Avoid_: Review, confirmation, approval

**Vertical Short Video**:
A 9:16 short-form video designed for social feeds, with Vietnamese narration and animated text.
_Avoid_: Reel, short, TikTok video

**Voiceover Provider**:
The speech generation service used to turn an approved script into narration audio.
_Avoid_: TTS engine, voice API, audio generator

**Production Run**:
A single attempt to produce a video from a Direct Source Request or a Selected Story.
_Avoid_: Job, render, session

**Pipeline Orchestrator**:
A CLI-level workflow coordinator that runs multiple phases of the **News-to-Video Pipeline** in order while tracking progress, writing artifacts, and stopping at explicit gates such as **Script Approval**.
_Avoid_: Automation, runner, batch script

**Pipeline Progress**:
The live CLI status output and append-only Production Run event log that records each pipeline phase as started, completed, failed, skipped, or waiting for approval.
_Avoid_: Logs, status messages, progress bar

**Pipeline Resume**:
The behavior where a **Pipeline Orchestrator** continues an existing **Production Run** by skipping already-created artifacts instead of overwriting them.
_Avoid_: Retry, rerun, restart

**Source-Grounded Script**:
An original video script written from verified source facts without copying long passages from the source material.
_Avoid_: Article summary, rewritten article, narration text

**Script Drafting Prompt**:
A reusable prompt package that instructs a human-operated chatbot or LLM to produce a script in the project's expected structure.
_Avoid_: Prompt, instruction, script template

**Script Drafting Provider**:
An adapter that calls a specific LLM service to produce or revise a **Source-Grounded Script** from **Source Evidence** and a **Script Drafting Prompt**.
_Avoid_: AI client, chatbot API, model wrapper

**Script Repair**:
The bounded retry step where a **Script Drafting Provider** revises a malformed **Source-Grounded Script** so it matches the expected artifact structure without adding unsupported facts.
_Avoid_: Auto-fix, rewrite, cleanup

**Duration Budget**:
The target and maximum runtime constraints that the script, storyboard, voiceover, and render must fit within.
_Avoid_: Video length, runtime limit, time cap

**Visual Treatment**:
A reusable style preset that defines text styling, color palette, motion, layout, and scene patterns for a video.
_Avoid_: Theme, template, design style

**Premium News Visual Treatment**:
A deterministic **Visual Treatment** for professional-looking news explainers, using motion-designed backgrounds, varied scene layouts, polished transitions, and accent highlights without requiring external B-roll or generated images.
_Avoid_: Fancy theme, pro template, cinematic mode

**Karaoke Caption**:
A time-synchronized text overlay that reveals only the currently spoken phrase and highlights the active spoken word or token as the voiceover progresses.
_Avoid_: Subtitle, full transcript, narration text

**Storyboard Artifact**:
The `STORYBOARD.md` production artifact that turns an approved script and voiceover timing into segment-by-segment visual instructions for a Vertical Short Video.
_Avoid_: Shot list, animation prompt, render config

**HyperFrames Composition**:
An HTML file with data-timed scenes (`data-start`, `data-duration`, `data-track-index`) that HyperFrames renders into an MP4 video using headless Chrome and FFmpeg.
_Avoid_: Video project, render config, animation HTML

**Curiosity-Driven News Explainer**:
A fast-paced but source-grounded editorial tone that creates curiosity without exaggerating the facts.
_Avoid_: Breaking news, viral script, clickbait

## Relationships

- A **News-to-Video Pipeline** starts from a news search request and ends with a rendered short video.
- A **News-to-Video Pipeline** presents multiple **News Candidates**.
- Each **News Candidate** must include **Source Evidence** before it can be shown for selection.
- Exactly one **News Candidate** becomes the **Selected Story** for a video production run.
- A **Direct Source Request** can produce a **Selected Story** without presenting multiple **News Candidates**.
- A **Discovery Request** produces multiple **News Candidates** before the user selects a **Selected Story**.
- A **Selected Story** must pass **Script Approval** before voiceover generation or rendering begins.
- The default output of the **News-to-Video Pipeline** is a **Vertical Short Video**.
- A **Voiceover Provider** produces the narration audio after **Script Approval**.
- A **Production Run** records the source evidence, script, storyboard, voiceover, composition files, and rendered output for one video.
- A **Pipeline Orchestrator** can advance a **Production Run** through multiple pipeline phases while preserving **Script Approval** as the default human gate.
- **Pipeline Progress** is recorded inside a **Production Run** so interrupted or failed orchestrated runs remain inspectable.
- **Pipeline Resume** never overwrites existing Production Run artifacts by default.
- **Script Approval** applies to a **Source-Grounded Script**.
- A **Source-Grounded Script** must fit the **Duration Budget** before **Script Approval**.
- A **Vertical Short Video** uses one **Visual Treatment**.
- A **Premium News Visual Treatment** improves perceived production quality while keeping the **HyperFrames Composition** deterministic and local-first.
- A **Karaoke Caption** depends on voiceover timing that is finer-grained than a whole script segment.
- A **Script Drafting Prompt** can produce a **Source-Grounded Script** from **Source Evidence**.
- A **Script Drafting Provider** uses a **Script Drafting Prompt** but may only produce or revise a **Source-Grounded Script**.
- **Script Repair** is bounded and must not bypass **Script Approval** by default.
- A **Storyboard Artifact** depends on an approved **Source-Grounded Script** and generated voiceover timing.
- A **Storyboard Artifact** prepares visual instructions for HyperFrames composition generation without containing render code.
- The default tone for a **Source-Grounded Script** is **Curiosity-Driven News Explainer**.

## Example dialogue

> **Dev:** "Does the **News-to-Video Pipeline** produce a video immediately after finding articles?"
> **Domain expert:** "No, it first presents news candidates so the user can select one."

## Flagged ambiguities

- The desired long-term output includes Vietnamese narration, but the MVP may use English narration through HyperFrames local TTS while keeping room for other voiceover providers.
- **Discovery Request** should search both English and Vietnamese sources by default; AI-related prompts may prioritize English sources when they are fresher or better sourced.
- The MVP starts with one default **Visual Treatment** and no presenter avatar; later versions may add topic-specific treatments.
- External chatbots should use **Script Drafting Prompt** to produce **Source-Grounded Script** only; storyboard and HyperFrames composition work belongs inside this repo.
