from pathlib import Path


def test_storyboard_workflow_documentation_covers_cli_and_artifact_contract() -> None:
    workflow = Path("docs/workflows/storyboard-workflow.md").read_text(
        encoding="utf-8"
    )
    artifact_contract = Path("docs/artifacts/storyboard.md").read_text(
        encoding="utf-8"
    )

    # Workflow covers prerequisites
    assert "Status: approved" in workflow
    assert "voiceover.json" in workflow

    # Workflow shows CLI command
    assert "hyperframe-video --storyboard <run-id>" in workflow

    # Workflow mentions generated file
    assert "STORYBOARD.md" in workflow
    assert "SCRIPT.md" in workflow

    # Workflow explains scope boundary
    assert "does **not**" in workflow
    assert "HyperFrames" in workflow
    assert "MP4" in workflow

    # Artifact contract covers scene fields
    assert "Segment ID" in artifact_contract
    assert "Start Time" in artifact_contract
    assert "Duration" in artifact_contract
    assert "Narration" in artifact_contract
    assert "On-screen Text" in artifact_contract
    assert "Visual Direction" in artifact_contract

    # Artifact contract covers rules
    assert "already exists" in artifact_contract
    assert "ai-modern" in artifact_contract
    assert "relative to the Production Run" in artifact_contract

    # Artifact contract covers scope boundary
    assert "does **not**" in artifact_contract
    assert "HyperFrames composition" in artifact_contract
