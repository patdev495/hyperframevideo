from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

from hyperframevideo.karaoke_captions import (
    KaraokeCaptionLoader,
    KaraokeCaptionManifest,
)
from hyperframevideo.models import NewsCandidate
from hyperframevideo.story_artifacts import StoryArtifacts


class ProductionRunExistsError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class VoiceoverManifestEntry:
    segment_id: str
    order: int
    narration_text: str
    audio_path: Path
    duration_seconds: float
    warnings: Sequence[str] = ()


@dataclass(frozen=True, slots=True)
class ProductionRun:
    run_id: str
    directory: Path

    @property
    def source_evidence_path(self) -> Path:
        return self.directory / "source-evidence.json"

    @property
    def candidates_path(self) -> Path:
        return self.directory / "candidates.json"

    @property
    def selected_story_path(self) -> Path:
        return self.directory / "SELECTED_STORY.md"

    @property
    def script_path(self) -> Path:
        return self.directory / "SCRIPT.md"

    @property
    def voiceover_manifest_path(self) -> Path:
        return self.directory / "voiceover.json"

    @property
    def voiceover_audio_dir(self) -> Path:
        return self.directory / "voiceover"

    @property
    def karaoke_captions_path(self) -> Path:
        return self.directory / "karaoke-captions.json"

    @property
    def storyboard_path(self) -> Path:
        return self.directory / "STORYBOARD.md"

    @property
    def composition_dir(self) -> Path:
        return self.directory / "composition"

    @property
    def render_output_path(self) -> Path:
        return self.directory / "output.mp4"

    @property
    def progress_log_path(self) -> Path:
        return self.directory / "progress.jsonl"


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

    def write_candidates(
        self,
        run: ProductionRun,
        candidates: Sequence[NewsCandidate],
        selected_candidate: NewsCandidate,
    ) -> None:
        selected_index = candidates.index(selected_candidate) + 1
        payload = {
            "selected_candidate": {
                "index": selected_index,
                "url": selected_candidate.url,
            },
            "candidates": [asdict(candidate) for candidate in candidates],
        }
        run.candidates_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def create_voiceover_audio_dir(self, run: ProductionRun) -> Path:
        run.voiceover_audio_dir.mkdir(parents=True, exist_ok=True)
        return run.voiceover_audio_dir

    def write_storyboard(
        self, run: ProductionRun, storyboard_markdown: str
    ) -> None:
        run.storyboard_path.write_text(storyboard_markdown, encoding="utf-8")

    def write_composition_html(
        self, run: ProductionRun, html_content: str
    ) -> None:
        run.composition_dir.mkdir(parents=True, exist_ok=True)
        (run.composition_dir / "index.html").write_text(
            html_content, encoding="utf-8"
        )

    def write_voiceover_manifest(
        self,
        run: ProductionRun,
        provider_name: str,
        entries: Sequence[VoiceoverManifestEntry],
    ) -> None:
        payload = {
            "provider_name": provider_name,
            "segments": [
                {
                    "segment_id": entry.segment_id,
                    "order": entry.order,
                    "narration_text": entry.narration_text,
                    "audio_path": entry.audio_path.relative_to(run.directory).as_posix(),
                    "duration_seconds": entry.duration_seconds,
                    "warnings": list(entry.warnings),
                }
                for entry in entries
            ],
        }
        run.voiceover_manifest_path.write_text(
            json.dumps(payload, indent=2), encoding="utf-8"
        )

    def write_karaoke_captions(
        self, run: ProductionRun, manifest: KaraokeCaptionManifest
    ) -> None:
        run.karaoke_captions_path.write_text(manifest.to_json(), encoding="utf-8")

    def read_karaoke_captions(
        self, run: ProductionRun
    ) -> KaraokeCaptionManifest | None:
        try:
            manifest_json = run.karaoke_captions_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

        return KaraokeCaptionLoader().load(manifest_json)
