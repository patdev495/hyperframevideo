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
