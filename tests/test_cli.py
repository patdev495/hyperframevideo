import pathlib
import subprocess
import sys


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
