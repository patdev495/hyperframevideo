from hyperframevideo.models import DirectSourceRequest, DiscoveryRequest, NewsCandidate


def test_direct_source_request_preserves_source_url() -> None:
    request = DirectSourceRequest(source_url="https://example.com/news/story")

    assert request.source_url == "https://example.com/news/story"


def test_discovery_request_default_candidate_count() -> None:
    request = DiscoveryRequest(query="AI news")

    assert request.query == "AI news"
    assert request.candidate_count == 5


def test_discovery_request_custom_candidate_count() -> None:
    request = DiscoveryRequest(query="Vietnam tech", candidate_count=10)

    assert request.candidate_count == 10


def test_news_candidate_with_all_fields() -> None:
    candidate = NewsCandidate(
        url="https://example.com/story",
        title="Example Story",
        source_name="Example News",
        published_at="2026-06-09",
        summary="A one-line summary.",
    )

    assert candidate.url == "https://example.com/story"
    assert candidate.source_name == "Example News"
    assert candidate.published_at == "2026-06-09"
    assert candidate.summary == "A one-line summary."


def test_news_candidate_accepts_missing_optional_fields() -> None:
    candidate = NewsCandidate(
        url="https://example.com/story",
        title="Example Story",
        source_name=None,
        published_at=None,
        summary=None,
    )

    assert candidate.source_name is None
    assert candidate.published_at is None
    assert candidate.summary is None


def test_models_are_frozen() -> None:
    request = DiscoveryRequest(query="test")
    candidate = NewsCandidate(
        url="https://x.com",
        title="T",
        source_name=None,
        published_at=None,
        summary=None,
    )

    import pytest

    with pytest.raises(AttributeError):
        request.query = "mutated"  # type: ignore[misc]

    with pytest.raises(AttributeError):
        candidate.url = "mutated"  # type: ignore[misc]


