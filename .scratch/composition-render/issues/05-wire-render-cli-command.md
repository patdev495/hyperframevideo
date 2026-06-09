Status: done

# Wire --render CLI command

## Parent

`.scratch/composition-render/PRD.md`

## What to build

Wire the **MP4 Render** phase into the CLI. Running `--render` for a **Production Run** with an existing `composition/` directory should verify system requirements, invoke `npx hyperframes render` as a subprocess, and write `output.mp4` into the **Production Run**.

## Acceptance criteria

- [ ] Running `hyperframe-video --render <run-id>` checks that `node`, `ffmpeg`, and `npx` are on `PATH` before rendering.
- [ ] Missing Node.js, FFmpeg, or npx produces a readable diagnostic without attempting to render.
- [ ] The command runs `npx hyperframes render` in the composition directory as a subprocess.
- [ ] On success, `output.mp4` exists in the **Production Run** directory.
- [ ] CLI output prints the MP4 path and a concise next-step message.
- [ ] Re-rendering fails with a readable diagnostic if `output.mp4` already exists.
- [ ] Missing composition directory fails with a readable diagnostic.
- [ ] HyperFrames render failure is reported with the subprocess stderr.
- [ ] Existing CLI flows remain unaffected.
- [ ] Tests verify system-requirement checks and subprocess invocation without running real HyperFrames (e.g., monkeypatch subprocess).

## Blocked by

- `.scratch/composition-render/issues/04-wire-compose-cli-command.md`
