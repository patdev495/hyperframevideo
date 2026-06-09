Status: done

# Scaffold Python CLI project with uv

## Parent

`.scratch/news-to-video-pipeline-mvp/PRD.md`

## What to build

Create the initial Python CLI project foundation for the **News-to-Video Pipeline** MVP. The project must use `uv` for environment and dependency management, expose a CLI entrypoint, establish typed model conventions for data crossing module boundaries, and include a basic automated test setup.

This slice should not implement source extraction or artifact generation yet. It should make the repo ready for later AFK issues to add the **Production Run Store**, **Source Extractor**, and CLI orchestration without reopening project structure decisions.

## Acceptance criteria

- [x] The repo has a `uv`-managed Python project configuration.
- [x] A CLI command can be invoked locally and returns a basic help or version response.
- [x] The project has a clear source package layout for the News-to-Video Pipeline.
- [x] Typed models are available for future module boundary data.
- [x] A test runner is configured and can run at least one passing smoke test.
- [x] Documentation or README notes explain the basic local setup command.

## Blocked by

None - can start immediately
