from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from hyperframevideo.models import NewsCandidate


@dataclass(frozen=True, slots=True)
class NewsCandidateBuilder:
    def build(self, raw_results: Sequence[Mapping[str, Any]]) -> list[NewsCandidate]:
        return [
            NewsCandidate(
                url=str(raw["url"]),
                title=str(raw["title"]),
                source_name=str(raw["source"]),
                published_at=self._optional_text(raw.get("date")),
                summary=self._summary(raw.get("body")),
            )
            for raw in raw_results
        ]

    def _optional_text(self, value: object) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text if text else None

    def _summary(self, value: object) -> str | None:
        text = self._optional_text(value)
        if text is None:
            return None

        sentence_match = re.match(r"^.+?[.!?](?:\s|$)", text)
        if sentence_match:
            return sentence_match.group(0).strip()

        if len(text) <= 150:
            return text
        return text[:147].rstrip() + "..."
