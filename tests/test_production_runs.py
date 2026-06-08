from pathlib import Path

import pytest

from hyperframevideo.production_runs import ProductionRunExistsError, ProductionRunStore


def test_create_production_run_returns_artifact_paths(tmp_path: Path) -> None:
    store = ProductionRunStore(root=tmp_path / ".runs")

    run = store.create(run_id="run-001")

    assert run.run_id == "run-001"
    assert run.directory == tmp_path / ".runs" / "run-001"
    assert run.source_evidence_path == run.directory / "source-evidence.json"
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
