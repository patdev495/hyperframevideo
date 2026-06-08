from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ProductionRunExistsError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class ProductionRun:
    run_id: str
    directory: Path

    @property
    def source_evidence_path(self) -> Path:
        return self.directory / "source-evidence.json"

    @property
    def selected_story_path(self) -> Path:
        return self.directory / "SELECTED_STORY.md"

    @property
    def script_path(self) -> Path:
        return self.directory / "SCRIPT.md"


@dataclass(frozen=True, slots=True)
class ProductionRunStore:
    root: Path = Path(".runs")

    def create(self, run_id: str) -> ProductionRun:
        run = ProductionRun(run_id=run_id, directory=self.root / run_id)

        try:
            run.directory.mkdir(parents=True, exist_ok=False)
        except FileExistsError as error:
            raise ProductionRunExistsError(f"Production Run already exists: {run_id}") from error

        return run
