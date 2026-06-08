from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hyperframevideo.models import ExtractedSource


@dataclass(frozen=True, slots=True)
class SourceEvidence:
    url: str
    title: str
    source_name: str | None
    published_at: str | None
    extracted_text: str
    extraction_method: str
    warnings: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "source_name": self.source_name,
            "published_at": self.published_at,
            "extracted_text": self.extracted_text,
            "extraction_method": self.extraction_method,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True, slots=True)
class SourceEvidenceBuilder:
    minimum_text_length: int = 120

    def build(self, extracted: ExtractedSource) -> SourceEvidence:
        warnings = list(extracted.warnings)
        if not extracted.title.strip():
            warnings.append("missing-title")
        if extracted.published_at is None:
            warnings.append("missing-publish-date")
        if len(extracted.text.strip()) < self.minimum_text_length:
            warnings.append("low-content")

        return SourceEvidence(
            url=extracted.source_url,
            title=extracted.title,
            source_name=extracted.source_name,
            published_at=extracted.published_at,
            extracted_text=extracted.text,
            extraction_method=extracted.extraction_method,
            warnings=tuple(warnings),
        )
