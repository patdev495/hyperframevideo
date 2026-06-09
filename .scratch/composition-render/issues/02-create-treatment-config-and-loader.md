Status: done

# Create treatment config and loader

## Parent

`.scratch/composition-render/PRD.md`

## What to build

Add a `treatments.json` config file that maps **Visual Treatment** names to HTML/CSS parameters (colors, fonts, text sizes, transition durations, layout classes). Add a typed loader that reads this config and returns treatment parameters for composition generation.

This slice should not generate HTML or call HyperFrames. It only provides the typed treatment config.

## Acceptance criteria

- [ ] A default `treatments.json` ships with the project containing one entry (`ai-modern`).
- [ ] Each treatment entry includes: name, background color, text color, accent color, font family, title font size, body font size, fade-in duration, and slide-up duration.
- [ ] A typed loader reads the JSON and returns a `TreatmentConfig` dataclass for a named treatment.
- [ ] An unknown treatment name produces a readable diagnostic.
- [ ] A malformed JSON file produces a readable diagnostic.
- [ ] Tests verify treatment loading with fixture JSON payloads.

## Blocked by

- `.scratch/composition-render/issues/01-extend-store-for-composition-paths.md`
