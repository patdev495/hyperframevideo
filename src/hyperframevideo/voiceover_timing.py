from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


class VoiceoverTimingError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class VoiceoverTimingEntry:
    segment_id: str
    order: int
    narration_text: str
    audio_path: str
    duration_seconds: float
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class VoiceoverTimingLoader:
    def load(self, manifest_json: str) -> list[VoiceoverTimingEntry]:
        try:
            payload = json.loads(manifest_json)
        except json.JSONDecodeError as error:
            raise VoiceoverTimingError(f"Invalid voiceover.json: {error.msg}.") from error

        if not isinstance(payload, dict):
            raise VoiceoverTimingError("voiceover.json must contain a JSON object.")
        if not payload.get("provider_name"):
            raise VoiceoverTimingError("voiceover.json is missing provider_name.")
        segments = payload.get("segments")
        if not isinstance(segments, list):
            raise VoiceoverTimingError("voiceover.json is missing segments.")

        entries = [
            self._load_segment(segment, index=index)
            for index, segment in enumerate(segments, start=1)
        ]
        return sorted(entries, key=lambda entry: entry.order)

    def _load_segment(self, segment: Any, index: int) -> VoiceoverTimingEntry:
        if not isinstance(segment, dict):
            raise VoiceoverTimingError(f"Voiceover segment {index} must be an object.")

        segment_id = self._required_string(segment, "segment_id", index)
        order = self._required_int(segment, "order", index)
        narration_text = self._required_string(segment, "narration_text", index)
        audio_path = self._required_string(segment, "audio_path", index)
        duration_seconds = self._required_number(
            segment, "duration_seconds", index
        )
        if duration_seconds <= 0:
            raise VoiceoverTimingError(
                f"Voiceover segment {index} duration_seconds must be positive."
            )

        warnings = segment.get("warnings", [])
        if not isinstance(warnings, list) or not all(
            isinstance(warning, str) for warning in warnings
        ):
            raise VoiceoverTimingError(
                f"Voiceover segment {index} warnings must be a list of strings."
            )

        return VoiceoverTimingEntry(
            segment_id=segment_id,
            order=order,
            narration_text=narration_text,
            audio_path=audio_path,
            duration_seconds=duration_seconds,
            warnings=tuple(warnings),
        )

    def _required_string(self, segment: dict[str, Any], field: str, index: int) -> str:
        value = segment.get(field)
        if not isinstance(value, str) or not value:
            raise VoiceoverTimingError(
                f"Voiceover segment {index} is missing {field}."
            )
        return value

    def _required_int(self, segment: dict[str, Any], field: str, index: int) -> int:
        value = segment.get(field)
        if not isinstance(value, int):
            raise VoiceoverTimingError(
                f"Voiceover segment {index} is missing {field}."
            )
        return value

    def _required_number(self, segment: dict[str, Any], field: str, index: int) -> float:
        value = segment.get(field)
        if not isinstance(value, int | float):
            raise VoiceoverTimingError(
                f"Voiceover segment {index} is missing {field}."
            )
        return float(value)
