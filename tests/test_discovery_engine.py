import pytest

from hyperframevideo.discovery_engine import DiscoveryEngine, DiscoverySearchError
from hyperframevideo.models import DiscoveryRequest


class FakeDuckDuckGo:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def news(self, query: str, max_results: int) -> list[dict[str, str]]:
        self.calls.append((query, max_results))
        return [
            {"title": "Story 1", "url": "https://example.com/1"},
            {"title": "Story 2", "url": "https://example.com/2"},
        ]


def test_discovery_engine_returns_raw_news_results_with_requested_count() -> None:
    client = FakeDuckDuckGo()
    engine = DiscoveryEngine(client_factory=lambda: client)

    results = engine.search(DiscoveryRequest(query="AI video", candidate_count=2))

    assert results == [
        {"title": "Story 1", "url": "https://example.com/1"},
        {"title": "Story 2", "url": "https://example.com/2"},
    ]
    assert client.calls == [("AI video", 2)]


class FailingDuckDuckGo:
    def news(self, query: str, max_results: int) -> list[dict[str, str]]:
        raise OSError("connection reset")


def test_discovery_engine_raises_readable_search_error() -> None:
    engine = DiscoveryEngine(client_factory=FailingDuckDuckGo)

    with pytest.raises(DiscoverySearchError, match="Failed to search news for: AI video"):
        engine.search(DiscoveryRequest(query="AI video", candidate_count=3))
