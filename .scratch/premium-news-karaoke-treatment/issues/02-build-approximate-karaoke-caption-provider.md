Status: done

# Build approximate Karaoke Caption provider

## Parent

.scratch/premium-news-karaoke-treatment/PRD.md

## What to build

Add the first **Karaoke Caption** timing provider. It should derive approximate word timings from each script narration segment and the segment duration already recorded in `voiceover.json`.

This provider is the MVP timing source. It should be deterministic, local-first, and replaceable by a future Whisper-based precise provider.

## Acceptance criteria

- [ ] The provider accepts narration text and segment duration.
- [ ] The provider emits ordered segment-relative caption tokens using the shared timing contract.
- [ ] The provider handles Vietnamese text, English text, punctuation, and mixed-language narration.
- [ ] The generated token timings are monotonic and cover the segment duration.
- [ ] Re-running the provider with the same input produces identical timing.
- [ ] Tests document the expected timing approximation behavior.

## Blocked by

- .scratch/premium-news-karaoke-treatment/issues/01-add-karaoke-caption-timing-contract.md
