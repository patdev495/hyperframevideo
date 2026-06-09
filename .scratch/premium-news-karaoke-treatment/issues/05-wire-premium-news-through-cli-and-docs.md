Status: done

# Wire Premium News treatment through CLI and docs

## Parent

.scratch/premium-news-karaoke-treatment/PRD.md

## What to build

Make the new `premium-news` **Visual Treatment** usable through the existing pipeline flow. A user should be able to set `Visual Treatment: premium-news` in `SCRIPT.md`, approve the script, generate voiceover, storyboard, composition, and render using the same CLI commands as before.

Update workflow and artifact documentation so the user understands how **Karaoke Caption** timing is generated now and how precise timing can replace it later.

## Acceptance criteria

- [ ] The storyboard/composition flow preserves `Visual Treatment: premium-news`.
- [ ] The compose command uses the `premium-news` renderer when the storyboard requests it.
- [ ] Documentation explains that approximate caption timing is the initial provider.
- [ ] Documentation explains that Whisper timing is a future provider, not part of this issue.
- [ ] CLI tests cover the `premium-news` treatment path.
- [ ] Existing CLI tests for `ai-modern` still pass.

## Blocked by

- .scratch/premium-news-karaoke-treatment/issues/04-add-premium-news-visual-treatment-composition.md
