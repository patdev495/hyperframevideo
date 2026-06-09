Status: ready-for-agent

# Extract script storyboard scenes

## Parent

`.scratch/storyboard-artifact/PRD.md`

## What to build

Add a script storyboard extractor that parses approved `SCRIPT.md` content into ordered scene inputs. Each `## Segment N` block should produce scene text fields used by the **Storyboard Artifact**: narration, on-screen text, purpose, facts used, and stable segment ID.

This extractor should not know about file paths, voiceover audio, `voiceover.json`, HyperFrames, or `STORYBOARD.md` output formatting.

## Acceptance criteria

- [ ] Approved script content with multiple `## Segment N` blocks produces ordered typed scene inputs.
- [ ] Scene IDs are stable and based on script order, such as `segment-001`.
- [ ] The extractor supports both inline and multiline `Narration:` values.
- [ ] `On-screen text:`, `Purpose:`, and `Facts used:` are parsed when present.
- [ ] Missing narration or missing on-screen text produces readable diagnostics.
- [ ] Tests use script markdown fixtures and verify observable scene output.

## Blocked by

- `.scratch/storyboard-artifact/issues/02-load-and-validate-voiceover-timing.md`
