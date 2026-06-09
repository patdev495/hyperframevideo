# Pipeline Orchestrator with Script Drafting Providers

Status: accepted

The project will add a **Pipeline Orchestrator** CLI flow that can run multiple **News-to-Video Pipeline** phases end to end while recording **Pipeline Progress** and preserving **Script Approval** as the default human gate. Unlike the MVP's manual chatbot workflow, the orchestrator may call app-owned **Script Drafting Providers** such as DeepSeek to draft or repair `SCRIPT.md`, but those providers remain scoped to **Source-Grounded Script** work only; storyboard, voiceover, composition, and rendering stay inside this repository.

**Consequences**

- The default orchestrated run stops at `script_approval`; `--auto-approve-script` is required to proceed without human review.
- Render remains opt-in with a separate render flag because it depends on local Node.js, npx, and FFmpeg.
- Progress is both displayed live in the CLI and appended to the Production Run as `progress.jsonl`.
- Existing artifacts are not overwritten by default; **Pipeline Resume** skips completed phases.
- DeepSeek is the first **Script Drafting Provider**, configured with environment variables and optional CLI model override.
