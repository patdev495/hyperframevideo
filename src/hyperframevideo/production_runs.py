from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hyperframevideo.story_artifacts import StoryArtifacts


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

    def write_story_artifacts(
        self, run: ProductionRun, artifacts: StoryArtifacts
    ) -> None:
        run.selected_story_path.write_text(
            artifacts.selected_story_markdown, encoding="utf-8"
        )
        run.script_path.write_text(artifacts.script_markdown, encoding="utf-8")
