Status: done

# Persist Karaoke Caption timing for Production Runs

## Parent

.scratch/premium-news-karaoke-treatment/PRD.md

## What to build

Extend the **Production Run** artifact flow so generated **Karaoke Caption** timing can be stored and reused by downstream composition generation. The artifact contract must remain backward-compatible with existing production runs and existing `ai-modern` behavior.

The stored timing should be provider-neutral so approximate timing can be replaced later by Whisper timing without changing the composition renderer.

## Acceptance criteria

- [ ] A production run can store caption timing for each voiceover segment.
- [ ] Existing runs without caption timing still work for existing flows.
- [ ] Caption timing can be loaded by the composition phase.
- [ ] The artifact records the timing source, such as approximate timing.
- [ ] Tests cover writing, reading, missing data, and backward compatibility.

## Blocked by

- .scratch/premium-news-karaoke-treatment/issues/01-add-karaoke-caption-timing-contract.md
- .scratch/premium-news-karaoke-treatment/issues/02-build-approximate-karaoke-caption-provider.md
