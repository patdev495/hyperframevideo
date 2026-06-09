# Pipeline Orchestrator Workflow

The `hyperframe-video run` command creates or resumes a **Production Run**, records **Pipeline Progress**, and coordinates the News-to-Video Pipeline phases from a Direct Source Request.

## Default Run to Script Approval

Use the default flow when the script needs human review before downstream artifacts are created:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi
```

This creates or resumes:

```text
.runs/demo-001/
|-- source-evidence.json
|-- SELECTED_STORY.md
|-- SCRIPT.md
`-- progress.jsonl
```

The default flow stops at **Script Approval**. `SCRIPT.md` remains:

```text
Status: draft
```

Review the script against `source-evidence.json`. Downstream phases do not run until the script is approved or a newly drafted script is explicitly auto-approved.

Use `--language vi` for Vietnamese scripts or `--language en` for English scripts. The selected language is injected into the **Script Drafting Prompt**, and the generated `SCRIPT.md` should use the matching `Language:` header and audience-facing text.

## DeepSeek Setup

DeepSeek is the first **Script Drafting Provider**. Configure credentials through environment variables:

```powershell
$env:DEEPSEEK_API_KEY = "your-api-key"
```

Optional settings:

```powershell
$env:DEEPSEEK_BASE_URL = "https://api.deepseek.com"
$env:DEEPSEEK_MODEL = "deepseek-chat"
```

Override the model for one run:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --script-model deepseek-reasoner
```

Script Drafting Providers may only draft or repair **Source-Grounded Script** artifacts from **Source Evidence** and the **Script Drafting Prompt**. They must not create `STORYBOARD.md`, `composition/index.html`, render code, or voiceover manifests.

## Auto-Approve Through Compose

For trusted batch runs, auto-approve the newly drafted script and continue through voiceover, storyboard, and composition:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --auto-approve-script
```

This changes the newly drafted script to:

```text
Status: approved
```

Then it creates:

```text
.runs/demo-001/voiceover.json
.runs/demo-001/voiceover/
.runs/demo-001/STORYBOARD.md
.runs/demo-001/composition/index.html
```

Rendering does not run by default.

## Render Opt-In

Rendering requires Node.js, `npx`, and FFmpeg on `PATH`. It only runs when requested:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --auto-approve-script --render
```

Successful render writes:

```text
.runs/demo-001/output.mp4
```

If Node.js, `npx`, or FFmpeg is missing, the orchestrator records a failed `render` progress event with a readable diagnostic.

## Pipeline Progress

Every orchestrated run appends events to:

```text
.runs/<run-id>/progress.jsonl
```

Each line is one JSON object with phase, status, timestamp, message, artifact path when available, provider/model metadata when available, and error diagnostics for failures.

Human-readable progress is printed by default:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi
```

Use JSONL for automation:

```powershell
uv run hyperframe-video run --url "https://example.com/news-story" --run-id demo-001 --script-provider deepseek --language vi --progress-format jsonl
```

## Safe Resume

Rerun the same command with the same `--run-id` to resume. Existing artifacts are skipped and are not overwritten:

- Existing `source-evidence.json` skips source extraction.
- Existing draft `SCRIPT.md` stops again at **Script Approval**.
- Existing approved `SCRIPT.md` continues downstream.
- Existing `voiceover.json` skips voiceover.
- Existing `STORYBOARD.md` skips storyboard.
- Existing `composition/` skips compose.
- Existing `output.mp4` skips render.

Every skip is recorded in `progress.jsonl`.
