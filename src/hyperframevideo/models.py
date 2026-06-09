from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DirectSourceRequest:
    source_url: str


@dataclass(frozen=True, slots=True)
class ExtractedSource:
    source_url: str
    title: str
    text: str
    source_name: str | None
    published_at: str | None
    extraction_method: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DiscoveryRequest:
    query: str
    candidate_count: int = 5


@dataclass(frozen=True, slots=True)
class NewsCandidate:
    url: str
    title: str
    source_name: str | None
    published_at: str | None
    summary: str | None
