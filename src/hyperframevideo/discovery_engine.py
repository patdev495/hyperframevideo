from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

from hyperframevideo.models import DiscoveryRequest


class DiscoverySearchError(Exception):
    pass


class DuckDuckGoNewsClient(Protocol):
    def news(self, query: str, max_results: int) -> list[dict[str, Any]]:
        pass


def default_duckduckgo_client() -> DuckDuckGoNewsClient:
    from duckduckgo_search import DDGS

    return DDGS()


@dataclass(frozen=True, slots=True)
class DiscoveryEngine:
    client_factory: Callable[[], DuckDuckGoNewsClient] = field(
        default=default_duckduckgo_client
    )

    def search(self, request: DiscoveryRequest) -> list[dict[str, Any]]:
        client = self.client_factory()
        try:
            return list(client.news(request.query, max_results=request.candidate_count))
        except Exception as error:
            raise DiscoverySearchError(
                f"Failed to search news for: {request.query}"
            ) from error
