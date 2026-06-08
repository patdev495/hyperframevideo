from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DirectSourceRequest:
    source_url: str
