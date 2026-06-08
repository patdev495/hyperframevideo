Status: ready-for-agent

# Record future extension contracts

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Record lightweight future extension contracts for the areas intentionally left out of the first MVP slice: **Voiceover Provider**, `STORYBOARD.md`, HyperFrames rendering, **Discovery Request**, and web UI. These should guide future issues without implementing the features prematurely.

The contracts should respect existing ADRs: HyperFrames is a dependency/rendering layer, the repo is local-first and CLI-first for MVP, JavaScript must be TypeScript, and any future frontend uses Vue and Tailwind CSS.

## Acceptance criteria

- [ ] There is a documented future **Voiceover Provider** contract that can support HyperFrames local TTS first and later Vietnamese providers.
- [ ] There is a documented `STORYBOARD.md` responsibility boundary distinct from `SCRIPT.md`.
- [ ] There is a documented HyperFrames render boundary that keeps orchestration in this repo.
- [ ] There is a documented **Discovery Request** boundary for future web search and News Candidate selection.
- [ ] There is a documented future web UI stack note: Vue and Tailwind CSS.
- [ ] The documentation does not implement TTS, rendering, Discovery Request, or web UI.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/06-add-script-approval-gate.md`
- `.scratch/news-to-video-pipeline-mvp/issues/07-wire-direct-source-to-draft-cli-flow.md`
