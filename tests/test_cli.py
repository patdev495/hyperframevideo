import json
import pathlib
import shutil
import subprocess
import sys
from io import StringIO

from hyperframevideo import cli
from hyperframevideo.vieneu_voiceover import VoiceoverOutput, VoiceoverProviderError


def test_cli_version_reports_package_version() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hyperframevideo.cli", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "hyperframevideo 0.1.0" in result.stdout


def test_cli_help_describes_news_to_video_pipeline() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "hyperframevideo.cli", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "News-to-Video Pipeline" in result.stdout


def test_cli_direct_source_to_draft_end_to_end(tmp_path: "pathlib.Path") -> None:
    # 1. Create a local fixture source
    source_html = """
    <html>
      <head>
        <title>End-to-end test story</title>
      </head>
      <body>
        <article>
          <h1>End-to-end test story</h1>
          <p>This is a test article used for an integration test.</p>
          <p>It needs enough text to avoid low-content warnings.</p>
          <p>We are verifying the direct source to draft CLI flow.</p>
        </article>
      </body>
    </html>
    """
    fixture_path = tmp_path / "fixture.html"
    fixture_path.write_text(source_html, encoding="utf-8")
    fixture_url = fixture_path.as_uri()

    # We will use tmp_path as our working directory so .runs is created inside it
    import os
    env = os.environ.copy()

    # 2. Run the CLI
    import subprocess
    import sys
    run_id = "test-run-01"
    result = subprocess.run(
        [sys.executable, "-m", "hyperframevideo.cli", fixture_url, "--run-id", run_id],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )

    # 3. Assertions
    assert result.returncode == 0
    assert "Production Run created:" in result.stdout

    run_dir = tmp_path / ".runs" / run_id
    assert run_dir.is_dir()

    evidence_path = run_dir / "source-evidence.json"
    selected_story_path = run_dir / "SELECTED_STORY.md"
    script_path = run_dir / "SCRIPT.md"

    assert evidence_path.is_file()
    assert selected_story_path.is_file()
    assert script_path.is_file()

    # Verify script content
    script_content = script_path.read_text(encoding="utf-8")
    assert "Status: draft" in script_content
    assert "End-to-end test story" in script_content


def test_cli_fails_gracefully_on_extraction_error_without_creating_run_dir(tmp_path: "pathlib.Path") -> None:
    import os
    env = os.environ.copy()
    import subprocess
    import sys

    run_id = "test-fail-01"
    # An invalid URL that will cause a SourceFetchError
    result = subprocess.run(
        [sys.executable, "-m", "hyperframevideo.cli", "https://invalid.example.com/missing", "--run-id", run_id],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 1
    assert "Error:" in result.stderr
    assert "Failed to fetch source URL" in result.stderr

    run_dir = tmp_path / ".runs" / run_id
    assert not run_dir.exists()


def test_cli_fails_gracefully_if_run_already_exists(tmp_path: "pathlib.Path") -> None:
    # Pre-create the run directory to force an error
    run_id = "test-conflict-01"
    run_dir = tmp_path / ".runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    # 1. Create a local fixture source (so extraction passes and it attempts to create run)
    source_html = "<html><head><title>Title</title></head><body><article><h1>Title</h1><p>Content to avoid warning.</p></article></body></html>"
    fixture_path = tmp_path / "fixture.html"
    fixture_path.write_text(source_html, encoding="utf-8")

    import os
    env = os.environ.copy()
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "hyperframevideo.cli", fixture_path.as_uri(), "--run-id", run_id],
        check=False,
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
    )

    assert result.returncode == 1
    assert "Error: Production Run already exists" in result.stderr

    # Assert that no artifacts were written to the existing directory
    assert not (run_dir / "source-evidence.json").exists()


def test_cli_discovery_request_to_draft_end_to_end(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    source_html = """
    <html>
      <head>
        <title>Discovery selected story</title>
      </head>
      <body>
        <article>
          <h1>Discovery selected story</h1>
          <p>This fixture story is selected from discovery candidates.</p>
          <p>It contains enough readable text for the extraction path.</p>
          <p>The test verifies discovery mode converges with direct source drafting.</p>
        </article>
      </body>
    </html>
    """
    fixture_path = tmp_path / "discovered.html"
    fixture_path.write_text(source_html, encoding="utf-8")

    class FakeDiscoveryEngine:
        def search(self, request):
            assert request.query == "AI video"
            assert request.candidate_count == 2
            return [
                {
                    "url": fixture_path.as_uri(),
                    "title": "Discovery selected story",
                    "source": "Fixture News",
                    "date": "2026-06-09",
                    "body": "A candidate summary.",
                }
            ]

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "DiscoveryEngine", FakeDiscoveryEngine)
    monkeypatch.setattr(sys, "stdin", StringIO("1\n"))

    result = cli.main(
        ["--discover", "AI video", "--candidates", "2", "--run-id", "discovery-run"]
    )

    assert result == 0
    stdout = capsys.readouterr().out
    assert "Production Run created:" in stdout
    assert "Next Step: Review the draft script at:" in stdout
    assert "To approve the script" in stdout
    run_dir = tmp_path / ".runs" / "discovery-run"
    assert (run_dir / "candidates.json").is_file()
    assert (run_dir / "source-evidence.json").is_file()
    assert (run_dir / "SELECTED_STORY.md").is_file()
    assert (run_dir / "SCRIPT.md").is_file()

    candidates = json.loads((run_dir / "candidates.json").read_text(encoding="utf-8"))
    assert candidates["selected_candidate"]["url"] == fixture_path.as_uri()
    assert candidates["candidates"][0]["title"] == "Discovery selected story"


def test_cli_discovery_request_reruns_search_when_selection_signals_rerun(
    tmp_path: "pathlib.Path", monkeypatch
) -> None:
    first_fixture = tmp_path / "first.html"
    first_fixture.write_text(
        "<html><body><article><h1>First story</h1><p>First batch.</p></article></body></html>",
        encoding="utf-8",
    )
    second_fixture = tmp_path / "second.html"
    second_fixture.write_text(
        """
        <html><body><article>
          <h1>Second story</h1>
          <p>The second batch contains the selected discovery story.</p>
          <p>It has enough readable text to complete the draft path.</p>
          <p>The re-run loop should use this candidate URL.</p>
        </article></body></html>
        """,
        encoding="utf-8",
    )

    class FakeDiscoveryEngine:
        calls = 0

        def search(self, request):
            FakeDiscoveryEngine.calls += 1
            if FakeDiscoveryEngine.calls == 1:
                return [
                    {
                        "url": first_fixture.as_uri(),
                        "title": "First story",
                        "source": "Fixture News",
                        "date": "2026-06-09",
                        "body": "First batch.",
                    }
                ]
            return [
                {
                    "url": second_fixture.as_uri(),
                    "title": "Second story",
                    "source": "Fixture News",
                    "date": "2026-06-09",
                    "body": "Second batch.",
                }
            ]

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "DiscoveryEngine", FakeDiscoveryEngine)
    monkeypatch.setattr(sys, "stdin", StringIO("0\n1\n"))

    result = cli.main(["--discover", "AI video", "--run-id", "rerun-run"])

    assert result == 0
    assert FakeDiscoveryEngine.calls == 2
    candidates = json.loads(
        (tmp_path / ".runs" / "rerun-run" / "candidates.json").read_text(
            encoding="utf-8"
        )
    )
    assert candidates["selected_candidate"]["url"] == second_fixture.as_uri()


def test_cli_discovery_request_fails_gracefully_when_no_candidates_are_found(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    class EmptyDiscoveryEngine:
        def search(self, request):
            return []

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "DiscoveryEngine", EmptyDiscoveryEngine)

    result = cli.main(["--discover", "missing topic", "--run-id", "empty-run"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "Error:" in stderr
    assert "No news candidates found for: missing topic" in stderr
    assert not (tmp_path / ".runs" / "empty-run").exists()


class FakeVoiceoverProvider:
    def synthesize(self, segments, audio_dir):
        audio_dir.mkdir(parents=True, exist_ok=True)
        outputs = []
        for segment in segments:
            audio_path = audio_dir / f"{segment.segment_id}.wav"
            audio_path.write_bytes(b"fake wav")
            outputs.append(
                VoiceoverOutput(
                    segment_id=segment.segment_id,
                    order=segment.order,
                    narration_text=segment.narration_text,
                    audio_path=audio_path,
                    duration_seconds=float(segment.order),
                    provider_name="fake-vieneu",
                    voice_config={"mode": "test", "voice_name": "fixture"},
                )
            )
        return outputs


class FailingVoiceoverProvider:
    def synthesize(self, segments, audio_dir):
        raise VoiceoverProviderError("provider setup failed")


def test_cli_voiceover_generates_manifest_and_audio_files_for_approved_run(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "approved-run"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        (
            "Status: approved\n"
            "Language: en\n\n"
            "## Segment 1\n"
            "Narration: First approved narration.\n\n"
            "## Segment 2\n"
            "Narration: Second approved narration."
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "VieNeuVoiceoverProvider", FakeVoiceoverProvider)

    result = cli.main(["--voiceover", "approved-run"])

    assert result == 0
    stdout = capsys.readouterr().out
    assert "Voiceover approved for Production Run: approved-run" in stdout
    assert "Extracted voiceover segments: 2" in stdout
    assert "Voiceover manifest:" in stdout
    assert "Next Step: Use voiceover.json for storyboard timing." in stdout

    manifest_path = run_dir / "voiceover.json"
    assert manifest_path.is_file()
    assert (run_dir / "voiceover" / "segment-001.wav").is_file()
    assert (run_dir / "voiceover" / "segment-002.wav").is_file()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload == {
        "provider_name": "fake-vieneu",
        "segments": [
            {
                "segment_id": "segment-001",
                "order": 1,
                "narration_text": "First approved narration.",
                "audio_path": "voiceover/segment-001.wav",
                "duration_seconds": 1.0,
                "warnings": [],
            },
            {
                "segment_id": "segment-002",
                "order": 2,
                "narration_text": "Second approved narration.",
                "audio_path": "voiceover/segment-002.wav",
                "duration_seconds": 2.0,
                "warnings": [],
            },
        ],
    }


def test_cli_voiceover_rejects_draft_script_without_writing_artifacts(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "draft-run"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: draft\nLanguage: en\n\n## Narration\nDraft narration.",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--voiceover", "draft-run"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "Error: Script is still draft." in stderr
    assert not (run_dir / "voiceover").exists()
    assert not (run_dir / "voiceover.json").exists()
    assert not (run_dir / "VOICEOVER.md").exists()


def test_cli_voiceover_rejects_missing_script_without_writing_artifacts(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "missing-script-run"
    run_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--voiceover", "missing-script-run"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "Error: SCRIPT.md not found for Production Run: missing-script-run" in stderr
    assert not (run_dir / "voiceover").exists()
    assert not (run_dir / "voiceover.json").exists()
    assert not (run_dir / "VOICEOVER.md").exists()


def test_cli_voiceover_rejects_approved_script_without_narration(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "no-narration-run"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: approved\nLanguage: en\n\n## Segment 1\nOn-screen text: Caption only.",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--voiceover", "no-narration-run"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "Error: Approved script contains no Narration lines." in stderr
    assert not (run_dir / "voiceover").exists()
    assert not (run_dir / "voiceover.json").exists()
    assert not (run_dir / "VOICEOVER.md").exists()


def test_cli_voiceover_rejects_rerun_when_artifacts_already_exist(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "rerun-voiceover"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: Approved narration.",
        encoding="utf-8",
    )
    (run_dir / "voiceover.json").write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "VieNeuVoiceoverProvider", FakeVoiceoverProvider)

    result = cli.main(["--voiceover", "rerun-voiceover"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert (
        "Error: Voiceover artifacts already exist for Production Run: rerun-voiceover"
        in stderr
    )


def test_cli_voiceover_allows_retry_after_empty_audio_dir_from_failed_setup(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "retry-voiceover"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: Approved narration.",
        encoding="utf-8",
    )
    (run_dir / "voiceover").mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "VieNeuVoiceoverProvider", FakeVoiceoverProvider)

    result = cli.main(["--voiceover", "retry-voiceover"])

    assert result == 0
    assert (run_dir / "voiceover.json").is_file()
    assert (run_dir / "voiceover" / "segment-001.wav").is_file()


def test_cli_voiceover_cleans_empty_audio_dir_after_provider_setup_failure(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "provider-failure"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: Approved narration.",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "VieNeuVoiceoverProvider", FailingVoiceoverProvider)

    result = cli.main(["--voiceover", "provider-failure"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "Error: provider setup failed" in stderr
    assert not (run_dir / "voiceover").exists()
    assert not (run_dir / "voiceover.json").exists()


def test_cli_storyboard_accepts_approved_run_with_voiceover_manifest(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "storyboard-run"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        (
            "Status: approved\nLanguage: en\n\n"
            "## Segment 1\n"
            "Narration: First approved narration.\n"
            "On-screen text: First screen.\n\n"
            "## Segment 2\n"
            "Narration: Second approved narration.\n"
            "On-screen text: Second screen."
        ),
        encoding="utf-8",
    )
    (run_dir / "voiceover.json").write_text(
        json.dumps({
            "provider_name": "fake",
            "segments": [
                {
                    "segment_id": "segment-001",
                    "order": 1,
                    "narration_text": "First approved narration.",
                    "audio_path": "voiceover/segment-001.wav",
                    "duration_seconds": 1.5,
                    "warnings": [],
                },
                {
                    "segment_id": "segment-002",
                    "order": 2,
                    "narration_text": "Second approved narration.",
                    "audio_path": "voiceover/segment-002.wav",
                    "duration_seconds": 2.0,
                    "warnings": [],
                },
            ],
        }),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--storyboard", "storyboard-run"])

    assert result == 0
    stdout = capsys.readouterr().out
    assert "Storyboard written to:" in stdout
    assert "STORYBOARD.md" in stdout
    assert (run_dir / "STORYBOARD.md").is_file()
    storyboard = (run_dir / "STORYBOARD.md").read_text(encoding="utf-8")
    assert "# Storyboard" in storyboard
    assert "Run ID: storyboard-run" in storyboard
    assert "## Scene 1" in storyboard
    assert "## Scene 2" in storyboard
    assert "First approved narration." in storyboard
    assert "Second approved narration." in storyboard
    assert "voiceover/segment-001.wav" in storyboard
    assert "voiceover/segment-002.wav" in storyboard


def test_cli_storyboard_preserves_script_visual_treatment(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "premium-storyboard"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        (
            "Status: approved\n"
            "Language: en\n"
            "Visual Treatment: premium-news\n\n"
            "## Segment 1\n"
            "Narration: Premium narration.\n"
            "On-screen text: Premium screen."
        ),
        encoding="utf-8",
    )
    (run_dir / "voiceover.json").write_text(
        json.dumps({
            "provider_name": "fake",
            "segments": [
                {
                    "segment_id": "segment-001",
                    "order": 1,
                    "narration_text": "Premium narration.",
                    "audio_path": "voiceover/segment-001.wav",
                    "duration_seconds": 1.5,
                    "warnings": [],
                },
            ],
        }),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--storyboard", "premium-storyboard"])

    assert result == 0
    storyboard = (run_dir / "STORYBOARD.md").read_text(encoding="utf-8")
    assert "Visual Treatment: premium-news" in storyboard


def test_cli_storyboard_rejects_rerun_when_storyboard_already_exists(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "rerun-storyboard"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: First.\nOn-screen text: Screen.",
        encoding="utf-8",
    )
    (run_dir / "voiceover.json").write_text(
        json.dumps({
            "provider_name": "fake",
            "segments": [
                {
                    "segment_id": "segment-001",
                    "order": 1,
                    "narration_text": "First.",
                    "audio_path": "voiceover/segment-001.wav",
                    "duration_seconds": 1.0,
                    "warnings": [],
                },
            ],
        }),
        encoding="utf-8",
    )
    (run_dir / "STORYBOARD.md").write_text("# Existing storyboard", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--storyboard", "rerun-storyboard"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "STORYBOARD.md already exists" in stderr


def test_cli_storyboard_rejects_draft_script_without_writing_artifact(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "draft-storyboard"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: draft\nLanguage: en\n\n## Segment 1\nNarration: Draft narration.",
        encoding="utf-8",
    )
    (run_dir / "voiceover.json").write_text(
        '{"provider_name": "fake", "segments": []}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--storyboard", "draft-storyboard"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert "Error: Script is still draft." in stderr
    assert not (run_dir / "STORYBOARD.md").exists()


def test_cli_storyboard_rejects_missing_script_without_writing_artifact(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "missing-script-storyboard"
    run_dir.mkdir(parents=True)
    (run_dir / "voiceover.json").write_text(
        '{"provider_name": "fake", "segments": []}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--storyboard", "missing-script-storyboard"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert (
        "Error: SCRIPT.md not found for Production Run: missing-script-storyboard"
        in stderr
    )
    assert not (run_dir / "STORYBOARD.md").exists()


def test_cli_storyboard_rejects_missing_voiceover_manifest_without_writing_artifact(
    tmp_path: "pathlib.Path", monkeypatch, capsys
) -> None:
    run_dir = tmp_path / ".runs" / "missing-voiceover-storyboard"
    run_dir.mkdir(parents=True)
    (run_dir / "SCRIPT.md").write_text(
        "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: Approved narration.",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    result = cli.main(["--storyboard", "missing-voiceover-storyboard"])

    assert result == 1
    stderr = capsys.readouterr().err
    assert (
        "Error: voiceover.json not found for Production Run: missing-voiceover-storyboard"
        in stderr
    )
    assert not (run_dir / "STORYBOARD.md").exists()


class TestCliCompose:
    """--compose generates composition/index.html from an approved run."""

    def _create_approved_run_with_storyboard(
        self, tmp_path: pathlib.Path, run_name: str, visual_treatment: str = "ai-modern"
    ) -> pathlib.Path:
        run_dir = tmp_path / ".runs" / run_name
        run_dir.mkdir(parents=True)
        (run_dir / "SCRIPT.md").write_text(
            "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: First approved narration.\nOn-screen text: First screen.\n",
            encoding="utf-8",
        )
        manifest = {
            "provider_name": "fake",
            "segments": [{
                "segment_id": "segment-001", "order": 1,
                "narration_text": "First approved narration.",
                "audio_path": "voiceover/segment-001.wav",
                "duration_seconds": 1.5, "warnings": [],
            }],
        }
        (run_dir / "voiceover.json").write_text(json.dumps(manifest), encoding="utf-8")
        (run_dir / "voiceover").mkdir(parents=True)
        (run_dir / "voiceover" / "segment-001.wav").write_bytes(b"fake audio")
        (run_dir / "STORYBOARD.md").write_text(
            f"# Storyboard\n\nRun ID: test-run\nVisual Treatment: {visual_treatment}\n\n## Scene 1\n",
            encoding="utf-8",
        )
        return run_dir

    def test_compose_creates_index_html_with_audio(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        self._create_approved_run_with_storyboard(tmp_path, "compose-run")

        result = cli.main(["--compose", "compose-run"])

        assert result == 0
        stdout = capsys.readouterr().out
        assert "composition/index.html" in stdout or "composition" in stdout
        index_path = tmp_path / ".runs" / "compose-run" / "composition" / "index.html"
        assert index_path.is_file()
        html = index_path.read_text(encoding="utf-8")
        assert "data-composition-id" in html
        assert "First approved narration." in html
        audio_dest = tmp_path / ".runs" / "compose-run" / "composition" / "voiceover" / "segment-001.wav"
        assert audio_dest.is_file()

    def test_compose_premium_news_creates_karaoke_caption_artifact_and_html(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(tmp_path)
        run_dir = self._create_approved_run_with_storyboard(
            tmp_path, "premium-compose", visual_treatment="premium-news"
        )

        result = cli.main(["--compose", "premium-compose"])

        assert result == 0
        captions_path = run_dir / "karaoke-captions.json"
        assert captions_path.is_file()
        captions = json.loads(captions_path.read_text(encoding="utf-8"))
        assert captions["timing_source"] == "approximate"
        assert captions["segments"][0]["segment_id"] == "segment-001"
        index_path = run_dir / "composition" / "index.html"
        html = index_path.read_text(encoding="utf-8")
        assert 'data-visual-treatment="premium-news"' in html
        assert "premium-bg-layer" in html
        assert "karaoke-caption" in html

    def test_compose_rejects_missing_storyboard(self, tmp_path, monkeypatch, capsys):
        run_dir = tmp_path / ".runs" / "no-storyboard"
        run_dir.mkdir(parents=True)
        (run_dir / "SCRIPT.md").write_text("Status: approved\nLanguage: en\n", encoding="utf-8")
        (run_dir / "voiceover.json").write_text('{"provider_name":"x","segments":[]}', encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        result = cli.main(["--compose", "no-storyboard"])

        assert result == 1
        stderr = capsys.readouterr().err
        assert "STORYBOARD.md" in stderr
        assert not (run_dir / "composition").exists()

    def test_compose_rejects_when_composition_exists(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        self._create_approved_run_with_storyboard(tmp_path, "existing-compose")
        (tmp_path / ".runs" / "existing-compose" / "composition").mkdir()
        (tmp_path / ".runs" / "existing-compose" / "composition" / "index.html").write_text("old")

        result = cli.main(["--compose", "existing-compose"])

        assert result == 1
        stderr = capsys.readouterr().err
        assert "already exists" in stderr


class TestCliRender:
    """--render runs npx hyperframes render and produces output.mp4."""

    def _create_composed_run(self, tmp_path: pathlib.Path, run_name: str) -> pathlib.Path:
        run_dir = tmp_path / ".runs" / run_name
        run_dir.mkdir(parents=True)
        (run_dir / "SCRIPT.md").write_text(
            "Status: approved\nLanguage: en\n\n## Segment 1\nNarration: Test.\nOn-screen text: Test.\n",
            encoding="utf-8",
        )
        manifest = {"provider_name": "fake", "segments": [{
            "segment_id": "segment-001", "order": 1,
            "narration_text": "Test.", "audio_path": "voiceover/segment-001.wav",
            "duration_seconds": 1.0, "warnings": [],
        }]}
        (run_dir / "voiceover.json").write_text(json.dumps(manifest), encoding="utf-8")
        (run_dir / "voiceover").mkdir()
        (run_dir / "voiceover" / "segment-001.wav").write_bytes(b"audio")
        (run_dir / "STORYBOARD.md").write_text(
            "# Storyboard\n\nRun ID: test\nVisual Treatment: ai-modern\n\n## Scene 1\n",
            encoding="utf-8",
        )
        (run_dir / "composition").mkdir()
        (run_dir / "composition" / "index.html").write_text(
            "<html>composition</html>", encoding="utf-8"
        )
        return run_dir

    def test_render_runs_subprocess_and_copies_mp4(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(tmp_path)
        self._create_composed_run(tmp_path, "render-run")
        calls = []

        def fake_run(*args, **kwargs):
            calls.append(args)
            # HyperFrames outputs to renders/composition_<timestamp>.mp4
            dest_dir = tmp_path / ".runs" / "render-run" / "composition"
            renders_dir = dest_dir / "renders"
            renders_dir.mkdir(exist_ok=True)
            (renders_dir / "composition_2026-06-09_12-00-00.mp4").write_bytes(b"fake mp4")
            return subprocess.CompletedProcess(args[0], 0, b"", b"")

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(shutil, "which", lambda cmd: f"/usr/bin/{cmd}")

        result = cli.main(["--render", "render-run"])

        assert result == 0
        stdout = capsys.readouterr().out
        assert "output.mp4" in stdout
        mp4_path = tmp_path / ".runs" / "render-run" / "output.mp4"
        assert mp4_path.is_file()

    def test_render_rejects_missing_composition(self, tmp_path, monkeypatch, capsys):
        run_dir = tmp_path / ".runs" / "no-composition"
        run_dir.mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        result = cli.main(["--render", "no-composition"])

        assert result == 1
        stderr = capsys.readouterr().err
        assert "composition" in stderr.lower()

    def test_render_rejects_when_output_exists(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        self._create_composed_run(tmp_path, "rerender-run")
        (tmp_path / ".runs" / "rerender-run" / "output.mp4").write_bytes(b"old")

        result = cli.main(["--render", "rerender-run"])

        assert result == 1
        stderr = capsys.readouterr().err
        assert "already exists" in stderr
