Status: done

# Wire storyboard command end-to-end

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Wire the **Storyboard Artifact** phase into a demoable CLI flow. Running the storyboard command for a **Production Run** with approved `SCRIPT.md` and `voiceover.json` should parse script scene inputs, load voiceover timing, align scenes, generate markdown, write `STORYBOARD.md`, and print the generated artifact path.

## Acceptance criteria

- [ ] Running the storyboard command against a valid run creates `STORYBOARD.md`.
- [ ] `STORYBOARD.md` includes one scene per voiceover segment.
- [ ] CLI output prints the storyboard path and a concise next-step message.
- [ ] Re-running the command fails with a readable diagnostic if `STORYBOARD.md` already exists.
- [ ] Draft scripts, malformed scripts, missing `voiceover.json`, or mismatched timing still fail without writing `STORYBOARD.md`.
- [ ] Existing Direct Source, Discovery Request, and Voiceover Provider CLI flows remain unaffected.
- [ ] An integration-style test covers approved script plus voiceover manifest to `STORYBOARD.md` using temporary run directories.

## Blocked by

- `.scratch/storyboard-artifact/issues/06-generate-storyboard-markdown.md`
