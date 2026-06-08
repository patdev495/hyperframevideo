# Script Drafting Prompt

Use this prompt with ChatGPT, Grok, or another chatbot when drafting `SCRIPT.md` outside this repo.

```text
You are writing a short-form news video script for a local HyperFrames production pipeline.

Your job is to produce SCRIPT.md only. Do not produce a storyboard, animation plan, shot list, or HTML. The script must be source-grounded: use only the facts provided in the source evidence, do not invent unsupported claims, and do not copy long passages from the original article.

Tone:
- Curiosity-driven news explainer
- Smart, fast-paced, and clear
- Engaging without being sensational or misleading

Video constraints:
- Language: English
- Format: vertical short video
- Target duration: 60-90 seconds
- Hard cap: 5 minutes
- Visual Treatment: ai-modern unless told otherwise

SCRIPT.md format:

Status: draft
Language: en
Target Duration: 60-90 seconds
Visual Treatment: ai-modern

# Title

Write a concise title.

# Hook

Write one strong opening sentence that creates curiosity without exaggerating.

# Source-Grounded Script

## Segment 1
Narration: Write spoken narration for this segment.
On-screen text: Write short punchy text suitable for kinetic typography or captions.
Purpose: Explain the role of this segment in the story.
Facts used:
- List the source facts used in this segment.

## Segment 2
Narration: ...
On-screen text: ...
Purpose: ...
Facts used:
- ...

Add as many segments as needed for the target duration. Keep segments short enough for a fast-paced short-form video.

# Fact Check

- Claim: Write an important factual claim from the script.
  Source: Cite the source URL or source evidence item that supports it.

# Production Notes

Mention any uncertainty, missing publication dates, weak sourcing, or facts that should be handled carefully.

Now write SCRIPT.md from this source evidence:

<PASTE SOURCE EVIDENCE HERE>
```
