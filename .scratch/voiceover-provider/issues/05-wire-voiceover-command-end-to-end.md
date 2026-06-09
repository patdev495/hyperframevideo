Status: done

# Wire Voiceover command end-to-end

## Parent

`.scratch/voiceover-provider/PRD.md`

## What to build

Wire the **Voiceover Provider** phase into a demoable CLI flow. Running the voiceover command for an approved **Production Run** should parse narration segments, call the VieNeu provider, write audio files, write `voiceover.json`, and print the generated artifact paths.

This is the first end-to-end tracer bullet from approved script to voiceover artifacts.

## Acceptance criteria

- [x] Running the voiceover command against an approved run creates `voiceover.json`.
- [x] The run contains one audio file per narration segment.
- [x] `voiceover.json` references all generated files using relative paths.
- [x] CLI output prints the manifest path and a concise next-step message.
- [x] Re-running the command has predictable behavior: either replaces owned voiceover artifacts or fails with a readable diagnostic.
- [x] Draft or malformed scripts still fail without writing voiceover artifacts.
- [x] An integration-style test covers approved script to manifest and audio files using a fake VieNeu provider.

## Blocked by

- `.scratch/voiceover-provider/issues/04-implement-vieneu-voiceover-provider.md`
