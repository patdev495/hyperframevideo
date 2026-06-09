import json
import pathlib
import subprocess
import sys
from io import StringIO

from hyperframevideo import cli


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
