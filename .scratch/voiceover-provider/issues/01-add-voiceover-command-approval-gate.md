Status: ready-for-agent

# Add Voiceover command approval gate

## Parent

`.scratch/voiceover-provider/PRD.md`

## What to build

Add the first vertical slice of the **Voiceover Provider** phase: a CLI voiceover command that targets an existing **Production Run**, loads its `SCRIPT.md`, and refuses to continue unless **Script Approval** has marked the script as approved.

This slice should not generate audio yet. It establishes the user-facing command, the run lookup behavior, and the approval failure behavior that all later voiceover work must preserve.

## Acceptance criteria

- [ ] The CLI exposes a voiceover command or mode that accepts a run ID.
- [ ] The command locates the target **Production Run** and reads `SCRIPT.md`.
- [ ] `Status: approved` allows the command to proceed to a placeholder success path.
- [ ] `Status: draft`, missing status, unsupported status, or missing `SCRIPT.md` produce readable diagnostics.
- [ ] Failure exits non-zero and writes no voiceover artifacts.
- [ ] Existing Direct Source and Discovery Request CLI flows are unaffected.
- [ ] Tests cover approved, draft, and missing-script behavior using temporary run directories.

## Blocked by

None - can start immediately
