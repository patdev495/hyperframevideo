from hyperframevideo.models import NewsCandidate
from hyperframevideo.news_candidate_builder import NewsCandidateBuilder


def test_news_candidate_builder_maps_duckduckgo_result_fields() -> None:
    raw_results = [
        {
            "url": "https://example.com/story",
            "title": "AI video tools get faster",
            "source": "Example News",
            "date": "2026-06-09T08:00:00Z",
            "body": "A new tool speeds up local video production.",
        }
    ]

    candidates = NewsCandidateBuilder().build(raw_results)

    assert candidates == [
        NewsCandidate(
            url="https://example.com/story",
            title="AI video tools get faster",
            source_name="Example News",
            published_at="2026-06-09T08:00:00Z",
            summary="A new tool speeds up local video production.",
        )
    ]


def test_news_candidate_builder_degrades_missing_optional_fields_to_none() -> None:
    raw_results = [
        {
            "url": "https://example.com/story",
            "title": "AI video tools get faster",
            "source": "Example News",
            "date": "",
        },
        {
            "url": "https://example.com/second",
            "title": "Second story",
            "source": "Another Source",
        },
    ]

    candidates = NewsCandidateBuilder().build(raw_results)

    assert candidates[0].published_at is None
    assert candidates[0].summary is None
    assert candidates[1].published_at is None
    assert candidates[1].summary is None


def test_news_candidate_builder_caps_long_summary_to_one_sentence() -> None:
    raw_results = [
        {
            "url": "https://example.com/story",
            "title": "AI video tools get faster",
            "source": "Example News",
            "date": "2026-06-09",
            "body": (
                "A new tool speeds up local video production. "
                "The company says creators can draft and render clips faster."
            ),
        }
    ]

    candidates = NewsCandidateBuilder().build(raw_results)

    assert candidates[0].summary == "A new tool speeds up local video production."
