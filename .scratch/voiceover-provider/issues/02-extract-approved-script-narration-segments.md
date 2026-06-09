Status: done

# Extract approved script narration segments

## Parent

`.scratch/voiceover-provider/PRD.md`

## What to build

Extend the voiceover command path so an approved `SCRIPT.md` is parsed into ordered voiceover segments. Each `Narration:` line becomes a typed segment with a stable segment ID, order number, and narration text.

This slice should make the command fail clearly when an approved script contains no narration lines, because downstream voiceover providers need real spoken text.

## Acceptance criteria

- [x] Approved `SCRIPT.md` content with multiple `Narration:` lines produces ordered typed voiceover segments.
- [x] Segment IDs are stable and based on script order, such as `segment-001`.
- [x] Blank narration text is ignored or rejected with a readable diagnostic.
- [x] Approved scripts with no narration fail with a readable diagnostic.
- [x] The extractor does not know about audio providers or file paths.
- [x] Tests use script markdown fixtures and verify observable segment output.

## Blocked by

- `.scratch/voiceover-provider/issues/01-add-voiceover-command-approval-gate.md`
