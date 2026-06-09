Status: done

# Wire --compose CLI command

## Parent

`.scratch/composition-render/PRD.md`

## What to build

Wire the **Composition Generation** phase into the CLI. Running `--compose` for a **Production Run** with approved `SCRIPT.md`, `voiceover.json`, and `STORYBOARD.md` should load treatment config, generate composition HTML, write `composition/index.html`, copy voiceover audio to the composition directory, and print the generated path.

## Acceptance criteria

- [ ] Running `hyperframe-video --compose <run-id>` creates `composition/index.html` with data-timed scenes.
- [ ] Voiceover audio files are copied to `composition/voiceover/` with relative paths matching the HTML.
- [ ] The composition uses the Visual Treatment from `STORYBOARD.md` header, falling back to `ai-modern`.
- [ ] Treatment parameters are loaded from `treatments.json`.
- [ ] CLI output prints the composition path and a concise next-step message.
- [ ] Re-running the command fails with a readable diagnostic if `composition/` already exists.
- [ ] Missing storyboard, missing voiceover manifest, unapproved script, or unknown treatment fail without writing composition files.
- [ ] Existing Direct Source, Discovery Request, Voiceover Provider, and Storyboard CLI flows remain unaffected.
- [ ] An integration-style test covers approved run to `composition/index.html` using temporary run directories.

## Blocked by

- `.scratch/composition-render/issues/03-generate-composition-html-from-storyboard.md`
