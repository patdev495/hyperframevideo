import json
from datetime import UTC, datetime
from pathlib import Path

from hyperframevideo.pipeline_progress import (
    PipelineProgressEvent,
    PipelineProgressLog,
    format_progress_jsonl,
    format_progress_text,
)


def test_progress_event_serializes_all_optional_fields() -> None:
    event = PipelineProgressEvent(
        phase="draft_script",
        status="completed",
        timestamp=datetime(2026, 6, 9, 8, 0, 0, tzinfo=UTC),
        message="Drafted SCRIPT.md",
        artifact_path=Path(".runs/run-001/SCRIPT.md"),
        provider_name="deepseek",
        model="deepseek-chat",
        error="",
    )

    assert event.to_json_dict() == {
        "phase": "draft_script",
        "status": "completed",
        "timestamp": "2026-06-09T08:00:00+00:00",
        "message": "Drafted SCRIPT.md",
        "artifact_path": ".runs/run-001/SCRIPT.md",
        "provider_name": "deepseek",
        "model": "deepseek-chat",
        "error": "",
    }


def test_progress_log_appends_and_reads_events(tmp_path: Path) -> None:
    log = PipelineProgressLog(tmp_path / ".runs" / "run-001" / "progress.jsonl")
    first = PipelineProgressEvent(phase="extract_source", status="started", message="Extracting")
    second = PipelineProgressEvent(
        phase="extract_source",
        status="completed",
        message="Wrote source evidence",
        artifact_path=Path("source-evidence.json"),
    )

    log.append(first)
    log.append(second)

    lines = log.path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert [event.phase for event in log.read()] == ["extract_source", "extract_source"]
    assert log.read()[1].artifact_path == Path("source-evidence.json")


def test_text_progress_format_is_human_readable() -> None:
    event = PipelineProgressEvent(
        phase="script_approval",
        status="waiting_for_approval",
        message="Review SCRIPT.md",
        artifact_path=Path(".runs/run-001/SCRIPT.md"),
    )

    assert format_progress_text(event) == (
        "[script_approval] waiting_for_approval - Review SCRIPT.md "
        "(.runs/run-001/SCRIPT.md)"
    )


def test_jsonl_progress_format_is_one_valid_json_object() -> None:
    event = PipelineProgressEvent(phase="render", status="failed", error="Missing ffmpeg")

    formatted = format_progress_jsonl(event)

    payload = json.loads(formatted)
    assert payload["phase"] == "render"
    assert payload["status"] == "failed"
    assert payload["error"] == "Missing ffmpeg"
    assert "\n" not in formatted
