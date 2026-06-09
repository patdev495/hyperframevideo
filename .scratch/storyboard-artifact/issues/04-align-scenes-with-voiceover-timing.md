Status: done

# Align scenes with voiceover timing

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Add a storyboard planning module that aligns typed script scene inputs with typed voiceover timing entries. It should compute cumulative start times and produce one storyboard scene per voiceover segment.

This slice should produce typed storyboard scene data only. It should not write files or generate markdown yet.

## Acceptance criteria

- [ ] Script scene inputs and voiceover timing entries align by segment ID.
- [ ] Each planned scene includes order, segment ID, start time, duration, audio path, narration text, on-screen text, purpose, and facts used.
- [ ] Start times are cumulative from `duration_seconds`.
- [ ] Missing timing entries, extra timing entries, duplicate segment IDs, or mismatched narration text produce readable diagnostics.
- [ ] Tests cover successful alignment and at least one mismatch diagnostic.

## Blocked by

- `.scratch/storyboard-artifact/issues/03-extract-script-storyboard-scenes.md`
