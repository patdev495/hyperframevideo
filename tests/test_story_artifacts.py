from hyperframevideo.source_evidence import SourceEvidence
from hyperframevideo.story_artifacts import StoryArtifactGenerator


def test_story_artifact_generator_creates_selected_story_and_draft_script() -> None:
    evidence = SourceEvidence(
        url="https://example.com/ai-story",
        title="AI model changes local video production",
        source_name="Example News",
        published_at="2026-06-08T08:00:00Z",
        extracted_text=(
            "A new AI model was released for local creative workflows. "
            "The report says small teams can use it to draft, edit, and render "
            "short-form media with fewer manual steps."
        ),
        extraction_method="readability",
        warnings=(),
    )
    generator = StoryArtifactGenerator()

    artifacts = generator.generate(evidence)

    assert "# Selected Story" in artifacts.selected_story_markdown
    assert "AI model changes local video production" in artifacts.selected_story_markdown
    assert "https://example.com/ai-story" in artifacts.selected_story_markdown

    script = artifacts.script_markdown
    assert script.startswith("Status: draft\nLanguage: en\n")
    assert "Target Duration: 60-90 seconds" in script
    assert "Visual Treatment: tech-hype" in script
    assert "# Title" in script
    assert "# Hook" in script
    assert "# Source-Grounded Script" in script
    assert "## Segment 1" in script
    assert "Narration:" in script
    assert "On-screen text:" in script
    assert "Purpose:" in script
    assert "Facts used:" in script
    assert "# Fact Check" in script
    assert "Source: https://example.com/ai-story" in script
    assert "# Production Notes" in script
