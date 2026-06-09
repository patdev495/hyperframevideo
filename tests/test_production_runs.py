import json
from pathlib import Path

import pytest

from hyperframevideo.models import NewsCandidate
from hyperframevideo.production_runs import ProductionRunExistsError, ProductionRunStore
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
