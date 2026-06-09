import json
import subprocess
from pathlib import Path

from hyperframevideo import cli
from hyperframevideo.models import DirectSourceRequest, ExtractedSource
from hyperframevideo.pipeline_orchestrator import (
    PipelineOrchestrator,
    PipelineRunRequest,
)
from hyperframevideo.production_runs import VoiceoverManifestEntry
from hyperframevideo.script_drafting import ScriptDraftingResult
from hyperframevideo.vieneu_voiceover import VoiceoverOutput


class FakeSourceExtractor:
    calls = 0

    def extract(self, request: DirectSourceRequest) -> ExtractedSource:
        self.calls += 1
        return ExtractedSource(
            source_url=request.source_url,
            title="Pipeline story",
            text="Pipeline source text with enough details for a grounded script.",
            source_name="Fixture News",
            published_at="2026-06-09",
            extraction_method="fixture",
            warnings=(),
        )


class FakeScriptProvider:
    provider_name = "fake-script"
    calls = 0
    last_prompt_text = ""

    def draft_script(self, source_evidence, prompt):
        self.calls += 1
        self.last_prompt_text = prompt.text
        return ScriptDraftingResult(
            script_markdown=_draft_script("draft"),
            provider_name="fake-script",
            model="fake-model",
            warnings=(),
            raw_usage={"total_tokens": 8},
        )

    def repair_script(self, malformed_script_markdown, source_evidence, prompt, *, max_attempts=1):
        raise AssertionError("repair not expected")


class FakeVoiceoverProvider:
    calls = 0

    def synthesize(self, segments, audio_dir):
        self.calls += 1
        outputs = []
        audio_dir.mkdir(parents=True, exist_ok=True)
        for segment in segments:
            audio_path = audio_dir / f"{segment.segment_id}.wav"
            audio_path.write_bytes(b"fake wav")
            outputs.append(
                VoiceoverOutput(
                    segment_id=segment.segment_id,
                    order=segment.order,
                    narration_text=segment.narration_text,
                    audio_path=audio_path,
                    duration_seconds=1.0,
                    provider_name="fake-voice",
                    voice_config={},
                )
            )
        return outputs


def _draft_script(status: str) -> str:
    return (
        f"Status: {status}\n"
        "Language: en\n"
        "Target Duration: 60-90 seconds\n"
        "Visual Treatment: ai-modern\n\n"
        "# Title\n\nPipeline story\n\n"
        "# Source-Grounded Script\n\n"
        "## Segment 1\n"
        "Narration: First approved narration.\n"
        "On-screen text: First screen.\n"
        "Purpose: Explain the story.\n"
        "Facts used:\n"
        "- Pipeline source fact.\n"
    )


def _orchestrator(tmp_path: Path, **kwargs) -> PipelineOrchestrator:
    return PipelineOrchestrator(
        runs_root=tmp_path / ".runs",
        source_extractor=kwargs.get("source_extractor", FakeSourceExtractor()),
        script_provider=kwargs.get("script_provider", FakeScriptProvider()),
        voiceover_provider=kwargs.get("voiceover_provider", FakeVoiceoverProvider()),
        tool_locator=kwargs.get("tool_locator", lambda name: f"/usr/bin/{name}"),
        process_runner=kwargs.get("process_runner"),
    )


def test_orchestrated_run_stops_at_script_approval_by_default(tmp_path: Path) -> None:
    events: list[str] = []
    orchestrator = _orchestrator(tmp_path)

    result = orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="run-001",
            progress_writer=events.append,
        )
    )

    run_dir = tmp_path / ".runs" / "run-001"
    assert result == 0
    assert (run_dir / "source-evidence.json").is_file()
    assert (run_dir / "SELECTED_STORY.md").is_file()
    assert (run_dir / "SCRIPT.md").read_text(encoding="utf-8").startswith("Status: draft")
    assert not (run_dir / "voiceover.json").exists()
    progress = [
        json.loads(line)
        for line in (run_dir / "progress.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert progress[-1]["phase"] == "script_approval"
    assert progress[-1]["status"] == "waiting_for_approval"
    assert any("[draft_script] completed" in line for line in events)


def test_orchestrated_run_passes_language_override_to_script_provider(
    tmp_path: Path,
) -> None:
    script_provider = FakeScriptProvider()
    orchestrator = _orchestrator(tmp_path, script_provider=script_provider)

    result = orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="vi-run",
            language="vi",
        )
    )

    assert result == 0
    assert "Vietnamese" in script_provider.last_prompt_text
    assert "Language: vi" in script_provider.last_prompt_text


def test_auto_approve_runs_through_compose_without_render(tmp_path: Path) -> None:
    orchestrator = _orchestrator(tmp_path)

    result = orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="auto-run",
            auto_approve_script=True,
        )
    )

    run_dir = tmp_path / ".runs" / "auto-run"
    assert result == 0
    assert (run_dir / "SCRIPT.md").read_text(encoding="utf-8").startswith("Status: approved")
    assert (run_dir / "voiceover.json").is_file()
    assert (run_dir / "STORYBOARD.md").is_file()
    assert (run_dir / "composition" / "index.html").is_file()
    assert not (run_dir / "output.mp4").exists()
    statuses = [
        (event["phase"], event["status"])
        for event in map(
            json.loads,
            (run_dir / "progress.jsonl").read_text(encoding="utf-8").splitlines(),
        )
    ]
    assert ("voiceover", "completed") in statuses
    assert ("storyboard", "completed") in statuses
    assert ("compose", "completed") in statuses


def test_render_opt_in_records_output_mp4(tmp_path: Path) -> None:
    def fake_process_runner(*args, **kwargs):
        renders = tmp_path / ".runs" / "render-run" / "composition" / "renders"
        renders.mkdir(parents=True, exist_ok=True)
        (renders / "composition_2026-06-09.mp4").write_bytes(b"mp4")
        return subprocess.CompletedProcess(args[0], 0, "", "")

    orchestrator = _orchestrator(tmp_path, process_runner=fake_process_runner)

    result = orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="render-run",
            auto_approve_script=True,
            render=True,
        )
    )

    run_dir = tmp_path / ".runs" / "render-run"
    assert result == 0
    assert (run_dir / "output.mp4").read_bytes() == b"mp4"
    render_events = [
        json.loads(line)
        for line in (run_dir / "progress.jsonl").read_text(encoding="utf-8").splitlines()
        if json.loads(line)["phase"] == "render"
    ]
    assert render_events[-1]["status"] == "completed"
    assert render_events[-1]["artifact_path"].endswith("output.mp4")


def test_render_missing_tools_records_failed_progress(tmp_path: Path) -> None:
    orchestrator = _orchestrator(tmp_path, tool_locator=lambda name: None)

    result = orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="missing-tools",
            auto_approve_script=True,
            render=True,
        )
    )

    assert result == 1
    run_dir = tmp_path / ".runs" / "missing-tools"
    failed = [
        json.loads(line)
        for line in (run_dir / "progress.jsonl").read_text(encoding="utf-8").splitlines()
        if json.loads(line)["status"] == "failed"
    ]
    assert failed[-1]["phase"] == "render"
    assert "Missing required tools" in failed[-1]["error"]


def test_resume_skips_existing_artifacts_without_overwriting(tmp_path: Path) -> None:
    source_extractor = FakeSourceExtractor()
    script_provider = FakeScriptProvider()
    voiceover_provider = FakeVoiceoverProvider()
    orchestrator = _orchestrator(
        tmp_path,
        source_extractor=source_extractor,
        script_provider=script_provider,
        voiceover_provider=voiceover_provider,
    )

    assert orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="resume-run",
            auto_approve_script=True,
        )
    ) == 0

    run_dir = tmp_path / ".runs" / "resume-run"
    original_evidence = (run_dir / "source-evidence.json").read_text(encoding="utf-8")
    original_script = (run_dir / "SCRIPT.md").read_text(encoding="utf-8")
    original_voiceover = (run_dir / "voiceover.json").read_text(encoding="utf-8")
    original_storyboard = (run_dir / "STORYBOARD.md").read_text(encoding="utf-8")
    original_composition = (run_dir / "composition" / "index.html").read_text(encoding="utf-8")

    assert orchestrator.run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="resume-run",
            auto_approve_script=True,
        )
    ) == 0

    assert source_extractor.calls == 1
    assert script_provider.calls == 1
    assert voiceover_provider.calls == 1
    assert (run_dir / "source-evidence.json").read_text(encoding="utf-8") == original_evidence
    assert (run_dir / "SCRIPT.md").read_text(encoding="utf-8") == original_script
    assert (run_dir / "voiceover.json").read_text(encoding="utf-8") == original_voiceover
    assert (run_dir / "STORYBOARD.md").read_text(encoding="utf-8") == original_storyboard
    assert (run_dir / "composition" / "index.html").read_text(encoding="utf-8") == original_composition
    progress = (run_dir / "progress.jsonl").read_text(encoding="utf-8")
    assert '"status":"skipped"' in progress


def test_resume_existing_draft_script_waits_for_approval(tmp_path: Path) -> None:
    run_dir = tmp_path / ".runs" / "draft-resume"
    run_dir.mkdir(parents=True)
    (run_dir / "source-evidence.json").write_text(
        json.dumps(
            {
                "url": "https://example.com/story",
                "title": "Existing",
                "source_name": "Fixture",
                "published_at": "2026-06-09",
                "extracted_text": "Existing evidence",
                "extraction_method": "fixture",
                "warnings": [],
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "SCRIPT.md").write_text(_draft_script("draft"), encoding="utf-8")

    result = _orchestrator(tmp_path).run(
        PipelineRunRequest(
            url="https://example.com/story",
            run_id="draft-resume",
            auto_approve_script=True,
        )
    )

    assert result == 0
    assert not (run_dir / "voiceover.json").exists()
    assert (run_dir / "SCRIPT.md").read_text(encoding="utf-8").startswith("Status: draft")


def test_cli_run_uses_orchestrator_with_jsonl_progress(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    class FakeOrchestrator:
        def __init__(self, *args, **kwargs):
            pass

        def run(self, request):
            assert request.url == "https://example.com/story"
            assert request.run_id == "cli-run"
            assert request.language == "vi"
            assert request.script_provider == "deepseek"
            assert request.progress_format == "jsonl"
            request.progress_writer('{"phase":"extract_source","status":"started"}')
            return 0

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "PipelineOrchestrator", FakeOrchestrator)

    result = cli.main(
        [
            "run",
            "--url",
            "https://example.com/story",
            "--run-id",
            "cli-run",
            "--language",
            "vi",
            "--script-provider",
            "deepseek",
            "--progress-format",
            "jsonl",
        ]
    )

    assert result == 0
    assert json.loads(capsys.readouterr().out)["phase"] == "extract_source"
