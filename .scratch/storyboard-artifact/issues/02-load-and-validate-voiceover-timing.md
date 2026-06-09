Status: done

# Load and validate voiceover timing

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Add a small voiceover timing loader that reads `voiceover.json` and returns typed timing entries for storyboard generation. The loader should validate the manifest shape, preserve segment order, and surface readable diagnostics for malformed timing data.

This slice should not know about `SCRIPT.md`, HyperFrames, or `STORYBOARD.md` formatting. It only turns the existing voiceover manifest contract into typed timing inputs.

## Acceptance criteria

- [x] A typed voiceover timing model exists for segment ID, order, narration text, audio path, duration seconds, and warnings.
- [x] Valid `voiceover.json` content loads into ordered timing entries.
- [x] Missing `provider_name`, missing `segments`, malformed segment entries, or non-positive durations produce readable diagnostics.
- [x] Audio paths remain relative strings from the manifest.
- [x] Tests use fixture manifest payloads and verify observable loader output and diagnostics.

## Blocked by

- `.scratch/storyboard-artifact/issues/01-add-storyboard-command-input-gates.md`
