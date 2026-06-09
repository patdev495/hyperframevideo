Status: done

# Prepare precise caption timing provider extension

## Parent

.scratch/premium-news-karaoke-treatment/PRD.md

## What to build

Document and test the extension seam for future precise **Karaoke Caption** timing providers, especially Whisper-based word timestamps. This issue should not implement Whisper. It should ensure the codebase has a clear provider boundary so later GPU-backed alignment work can plug in without redesigning the production-run artifacts or composition renderer.

## Acceptance criteria

- [ ] The caption timing provider interface can support approximate and precise providers.
- [ ] A test double can provide exact word timestamps and flow through composition generation.
- [ ] Documentation names Whisper as a future precise provider.
- [ ] The design does not require changing the **HyperFrames Composition** renderer when a precise provider is added.
- [ ] The current VieNeu SDK limitation is documented: installed `vieneu 3.0.4` does not expose a public word timestamp API.

## Blocked by

- .scratch/premium-news-karaoke-treatment/issues/05-wire-premium-news-through-cli-and-docs.md
