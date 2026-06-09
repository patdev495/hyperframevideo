Status: done

# Add Karaoke Caption timing contract

## Parent

.scratch/premium-news-karaoke-treatment/PRD.md

## What to build

Define the provider-neutral **Karaoke Caption** timing contract used by the **News-to-Video Pipeline**. The contract should represent word-level or token-level timing relative to a voiceover segment, while remaining independent from any specific timing source such as approximate timing, Whisper, or a future VieNeu timestamp API.

The contract should be suitable for serialization into production-run artifacts and consumption by the **HyperFrames Composition** generator.

## Acceptance criteria

- [ ] A caption timing model represents ordered caption tokens with text, start time, end time, and token order.
- [ ] Caption timing is segment-relative rather than globally absolute.
- [ ] The model can represent phrase windows for karaoke rendering without forcing the full narration to appear at once.
- [ ] Invalid timing data is rejected or reported clearly.
- [ ] Tests cover valid timing, empty timing, non-monotonic timing, and punctuation/Vietnamese text cases.

## Blocked by

None - can start immediately
