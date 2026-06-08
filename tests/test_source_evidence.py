import json

from hyperframevideo.models import ExtractedSource
from hyperframevideo.source_evidence import SourceEvidenceBuilder


def test_source_evidence_builder_normalizes_complete_extracted_source() -> None:
    extracted = ExtractedSource(
        source_url="https://example.com/ai-story",
        title="AI story",
        text=(
            "This article has enough extracted text to ground a short video script. "
            "It includes the central event, the actors involved, and the practical "
            "reason a viewer should care about the development."
        ),
        source_name="Example News",
        published_at="2026-06-08T08:00:00Z",
        extraction_method="readability",
    )
    builder = SourceEvidenceBuilder()

    evidence = builder.build(extracted)

    assert evidence.url == "https://example.com/ai-story"
    assert evidence.title == "AI story"
    assert evidence.source_name == "Example News"
    assert evidence.published_at == "2026-06-08T08:00:00Z"
    assert evidence.extracted_text == extracted.text
    assert evidence.extraction_method == "readability"
    assert evidence.warnings == ()
    assert json.loads(json.dumps(evidence.to_json_dict()))["url"] == evidence.url


def test_source_evidence_builder_warns_about_missing_metadata_and_low_content() -> None:
    extracted = ExtractedSource(
        source_url="https://example.com/thin-story",
        title="",
        text="Too short.",
        source_name=None,
        published_at=None,
        extraction_method="playwright",
    )
    builder = SourceEvidenceBuilder(minimum_text_length=40)

    evidence = builder.build(extracted)

    assert evidence.warnings == (
        "missing-title",
        "missing-publish-date",
        "low-content",
    )


def test_source_evidence_builder_preserves_extractor_warnings() -> None:
    extracted = ExtractedSource(
        source_url="https://example.com/ai-story",
        title="AI story",
        text="Enough text to avoid a low-content warning from the builder itself.",
        source_name="Example News",
        published_at="2026-06-08T08:00:00Z",
        extraction_method="readability",
        warnings=("used-browser-fallback",),
    )
    builder = SourceEvidenceBuilder(minimum_text_length=20)

    evidence = builder.build(extracted)

    assert evidence.warnings == ("used-browser-fallback",)
