from pathlib import Path


def test_voiceover_workflow_documentation_covers_cli_and_artifact_contract() -> None:
    workflow = Path("docs/workflows/voiceover-workflow.md").read_text(
        encoding="utf-8"
    )
    artifact_contract = Path("docs/artifacts/voiceover.md").read_text(
        encoding="utf-8"
    )

    assert "Status: approved" in workflow
    assert "hyperframe-video --voiceover <run-id>" in workflow
    assert "voiceover.json" in workflow
    assert "voiceover/segment-001.wav" in workflow
    assert "duration_seconds" in workflow
    assert "audio_path" in workflow
    assert "STORYBOARD.md" in workflow
    assert "VieNeu-TTS" in workflow
    assert "does not generate" in workflow
    assert "MP4" in workflow
    assert "voiceover.json" in artifact_contract
    assert "audio_path" in artifact_contract
    assert "duration_seconds" in artifact_contract
    assert "relative to the Production Run directory" in artifact_contract
