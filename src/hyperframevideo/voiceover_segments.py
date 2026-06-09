from __future__ import annotations

from dataclasses import dataclass


class VoiceoverNarrationError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class VoiceoverSegment:
    segment_id: str
    order: int
    narration_text: str


@dataclass(frozen=True, slots=True)
class VoiceoverNarrationExtractor:
    def extract(self, script_markdown: str) -> list[VoiceoverSegment]:
        segments: list[VoiceoverSegment] = []

        for line in script_markdown.splitlines():
            label, separator, value = line.strip().partition(":")
            if separator and label.strip().lower() == "narration":
                order = len(segments) + 1
                narration_text = value.strip()
                if not narration_text:
                    raise VoiceoverNarrationError(
                        f"Narration line {order} is blank."
                    )
                segments.append(
                    VoiceoverSegment(
                        segment_id=f"segment-{order:03d}",
                        order=order,
                        narration_text=narration_text,
                    )
                )

        if not segments:
            raise VoiceoverNarrationError(
                "Approved script contains no Narration lines."
            )

        return segments
