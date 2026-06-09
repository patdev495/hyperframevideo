import json
from pathlib import Path

import pytest

from hyperframevideo.models import NewsCandidate
from hyperframevideo.production_runs import (
    ProductionRunExistsError,
    ProductionRunStore,
    VoiceoverManifestEntry,
)
from hyperframevideo.story_artifacts import StoryArtifacts


def test_create_production_run_returns_artifact_paths(tmp_path: Path) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")

    run = store.create(run_id="run-001")

    assert run.run_id == "run-001"
    assert run.directory == tmp_path / ".runs" / "run-001"
    assert run.source_evidence_path == run.directory / "source-evidence.json"
    assert run.candidates_path == run.directory / "candidates.json"
    assert run.selected_story_path == run.directory / "SELECTED_STORY.md"
    assert run.script_path == run.directory / "SCRIPT.md"
    assert run.voiceover_manifest_path == run.directory / "voiceover.json"
    assert run.voiceover_audio_dir == run.directory / "voiceover"
    assert run.directory.is_dir()


def test_create_production_run_rejects_existing_run(tmp_path: Path) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")
    store.create(run_id="run-001")

    with pytest.raises(ProductionRunExistsError):
        store.create(run_id="run-001")


def test_default_store_creates_runs_under_runs_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    store = ProductionRunStore()

    run = store.create(run_id="deterministic-run")

    assert run.directory == Path(".runs") / "deterministic-run"
    assert run.directory.is_dir()


def test_write_story_artifacts_uses_production_run_paths(tmp_path: Path) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")
    run = store.create(run_id="run-001")
    artifacts = StoryArtifacts(
        selected_story_markdown="# Selected Story\n\nStory context.",
        script_markdown="Status: draft\nLanguage: en\n",
    )

    store.write_story_artifacts(run, artifacts)

    assert run.selected_story_path.read_text(encoding="utf-8") == (
        "# Selected Story\n\nStory context."
    )
    assert run.script_path.read_text(encoding="utf-8") == "Status: draft\nLanguage: en\n"


def test_create_direct_source_run_does_not_write_candidates_json(
    tmp_path: Path,
) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")
    run = store.create(run_id="run-001")

    assert not run.candidates_path.exists()


def test_create_voiceover_audio_dir_returns_owned_audio_directory(
    tmp_path: Path,
) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")
    run = store.create(run_id="run-001")

    audio_dir = store.create_voiceover_audio_dir(run)

    assert audio_dir == run.voiceover_audio_dir
    assert audio_dir.is_dir()


def test_write_candidates_records_presented_candidates_and_selection(
    tmp_path: Path,
) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")
    run = store.create(run_id="run-001")
    candidates = [
        NewsCandidate(
            url="https://example.com/one",
            title="Story One",
            source_name="Example News",
            published_at="2026-06-09",
            summary="First candidate.",
        ),
        NewsCandidate(
            url="https://example.com/two",
            title="Story Two",
            source_name=None,
            published_at=None,
            summary=None,
        ),
    ]

    store.write_candidates(run, candidates, selected_candidate=candidates[1])

    payload = json.loads(run.candidates_path.read_text(encoding="utf-8"))
    assert payload == {
        "selected_candidate": {
            "index": 2,
            "url": "https://example.com/two",
        },
        "candidates": [
            {
                "url": "https://example.com/one",
                "title": "Story One",
                "source_name": "Example News",
                "published_at": "2026-06-09",
                "summary": "First candidate.",
            },
            {
                "url": "https://example.com/two",
                "title": "Story Two",
                "source_name": None,
                "published_at": None,
                "summary": None,
            },
        ],
    }


def test_write_voiceover_manifest_records_provider_and_relative_audio_paths(
    tmp_path: Path,
) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")
    run = store.create(run_id="run-001")

    store.write_voiceover_manifest(
        run,
        provider_name="fake-provider",
        entries=[
            VoiceoverManifestEntry(
                segment_id="segment-001",
                order=1,
                narration_text="First narration.",
                audio_path=run.voiceover_audio_dir / "segment-001.wav",
                duration_seconds=1.25,
                warnings=(),
            ),
            VoiceoverManifestEntry(
                segment_id="segment-002",
                order=2,
                narration_text="Second narration.",
                audio_path=run.voiceover_audio_dir / "segment-002.wav",
                duration_seconds=2.5,
                warnings=("trimmed silence",),
            ),
        ],
    )

    payload = json.loads(run.voiceover_manifest_path.read_text(encoding="utf-8"))
    assert payload == {
        "provider_name": "fake-provider",
        "segments": [
            {
                "segment_id": "segment-001",
                "order": 1,
                "narration_text": "First narration.",
                "audio_path": "voiceover/segment-001.wav",
                "duration_seconds": 1.25,
                "warnings": [],
            },
            {
                "segment_id": "segment-002",
                "order": 2,
                "narration_text": "Second narration.",
                "audio_path": "voiceover/segment-002.wav",
                "duration_seconds": 2.5,
                "warnings": ["trimmed silence"],
            },
        ],
    }
