from pathlib import Path


def test_composition_workflow_documentation_covers_cli_and_artifact_contract() -> None:
    workflow = Path("docs/workflows/composition-render-workflow.md").read_text(
        encoding="utf-8"
    )
    artifact_contract = Path("docs/artifacts/composition.md").read_text(
        encoding="utf-8"
    )

    # Workflow covers prerequisites
    assert "Status: approved" in workflow
    assert "voiceover.json" in workflow
    assert "STORYBOARD.md" in workflow

    # Workflow shows CLI commands
    assert "hyperframe-video --compose <run-id>" in workflow
    assert "hyperframe-video --render <run-id>" in workflow

    # Workflow explains system requirements
    assert "Node.js" in workflow or "node" in workflow
    assert "FFmpeg" in workflow or "ffmpeg" in workflow
    assert "npx" in workflow

    # Workflow explains treatments config
    assert "treatments.json" in workflow
    assert "background_color" in workflow
    assert "premium-news" in workflow
    assert "karaoke-captions.json" in workflow
    assert "approximate" in workflow
    assert "Whisper" in workflow
    assert "vieneu 3.0.4" in workflow

    # Workflow covers scope boundary
    assert "does **not**" in workflow
    assert "B-roll" in workflow

    # Artifact contract covers format
    assert "data-composition-id" in artifact_contract
    assert "data-start" in artifact_contract
    assert "data-duration" in artifact_contract
    assert "data-track-index" in artifact_contract
    assert "GSAP" in artifact_contract
    assert "premium-news" in artifact_contract
    assert "Karaoke Caption" in artifact_contract
    assert "Whisper" in artifact_contract

    # Artifact contract covers layout
    assert "composition/index.html" in artifact_contract
    assert "voiceover/" in artifact_contract
    assert "1080" in artifact_contract
    assert "1920" in artifact_contract

    # Artifact contract covers scope boundary
    assert "does **not**" in artifact_contract
