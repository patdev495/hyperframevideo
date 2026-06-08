# Project technology constraints

Python code in this project will use `uv` for environment and dependency management, and data crossing module boundaries should use explicit typed models rather than loose dictionaries. JavaScript code must be TypeScript. If a frontend is added later, it will use Vue and Tailwind CSS so the web UI work has a clear default stack instead of reopening framework choices during implementation.
