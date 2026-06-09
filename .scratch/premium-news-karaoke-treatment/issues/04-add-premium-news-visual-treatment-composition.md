Status: done

# Add Premium News Visual Treatment composition

## Parent

.scratch/premium-news-karaoke-treatment/PRD.md

## What to build

Add a new **Premium News Visual Treatment** named `premium-news`. When selected, composition generation should produce a professional deterministic **HyperFrames Composition** with motion-designed backgrounds, scene transitions, short phrase caption windows, and active-word highlighting from **Karaoke Caption** timing.

The existing `ai-modern` treatment must continue working.

## Acceptance criteria

- [ ] `premium-news` is available as a selectable **Visual Treatment**.
- [ ] The generated composition uses layered animated backgrounds.
- [ ] The generated composition includes smooth scene transitions.
- [ ] The generated composition renders phrase-window karaoke captions rather than full narration text.
- [ ] The active caption token can be highlighted according to timing.
- [ ] The generated composition registers a seekable GSAP timeline on `window.__timelines`.
- [ ] The generated composition keeps audio in separate `<audio>` elements.
- [ ] Tests verify treatment-specific composition output without breaking `ai-modern`.

## Blocked by

- .scratch/premium-news-karaoke-treatment/issues/03-persist-caption-timing-for-production-runs.md
