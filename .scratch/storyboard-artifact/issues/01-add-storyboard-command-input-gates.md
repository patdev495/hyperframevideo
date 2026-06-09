Status: done

# Add storyboard command input gates

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Add the first vertical slice of the **Storyboard Artifact** phase: a CLI storyboard command or mode that targets an existing **Production Run**, loads its `SCRIPT.md`, refuses to continue unless **Script Approval** has marked the script as approved, and requires `voiceover.json` to exist.

This slice should not generate `STORYBOARD.md` yet. It establishes the user-facing command, run lookup behavior, approval gate, and missing-voiceover failure behavior that later storyboard work must preserve.

## Acceptance criteria

- [x] The CLI exposes a storyboard command or mode that accepts a run ID.
- [x] The command locates the target **Production Run** and reads `SCRIPT.md`.
- [x] `Status: approved` allows the command to proceed to a placeholder success path.
- [x] `Status: draft`, missing status, unsupported status, or missing `SCRIPT.md` produce readable diagnostics.
- [x] Missing `voiceover.json` produces a readable diagnostic.
- [x] Failure exits non-zero and writes no `STORYBOARD.md`.
- [x] Existing Direct Source, Discovery Request, and Voiceover Provider CLI flows are unaffected.
- [x] Tests cover approved, draft, missing-script, and missing-voiceover behavior using temporary run directories.

## Blocked by

None - can start immediately
