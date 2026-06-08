# SCRIPT.md

`SCRIPT.md` is the approved or draft narration artifact for a Production Run. It captures content, spoken narration, on-screen text, and source grounding; it does not define detailed animation or HyperFrames implementation.

## Format

```md
Status: draft
Language: en
Target Duration: 60-90 seconds
Visual Treatment: ai-modern

# Title

...

# Hook

...

# Source-Grounded Script

## Segment 1
Narration: ...
On-screen text: ...
Purpose: ...
Facts used:
- ...

## Segment 2
Narration: ...
On-screen text: ...
Purpose: ...
Facts used:
- ...

# Fact Check

- Claim: ...
  Source: ...

# Production Notes

...
```

## Rules

- `Status` starts as `draft` and must be changed to `approved` before voiceover generation or rendering.
- `Narration` is the spoken voiceover text.
- `On-screen text` is the short text that may appear in captions, headlines, or kinetic typography.
- `Purpose` explains why the segment exists in the story.
- `Facts used` must trace important claims back to Source Evidence.
- Detailed animation, transitions, layout, and HyperFrames-specific build instructions belong in `STORYBOARD.md`, not `SCRIPT.md`.
