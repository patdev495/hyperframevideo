Status: ready-for-agent

# Document portable Script Drafting Prompt workflow

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Document how a user can take Source Evidence from a **Production Run**, use `docs/prompts/script-drafting.md` with Codex, ChatGPT, Grok, or another chatbot, and paste the result back into `SCRIPT.md` while preserving the required script artifact structure.

The workflow must reinforce that external chatbots draft only the **Source-Grounded Script**; `STORYBOARD.md` and HyperFrames composition work stay inside this repo.

## Acceptance criteria

- [ ] Documentation explains where to find Source Evidence in a Production Run.
- [ ] Documentation explains how to use the portable Script Drafting Prompt.
- [ ] Documentation explains that the chatbot should output `SCRIPT.md` only.
- [ ] Documentation explains how to replace or edit a draft `SCRIPT.md`.
- [ ] Documentation explains that `Status` remains `draft` until the user approves it.
- [ ] Documentation points to `docs/artifacts/script.md` as the authoritative script format.

## Blocked by

- `.scratch/news-to-video-pipeline-mvp/issues/05-generate-selected-story-and-draft-script.md`
