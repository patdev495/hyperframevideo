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
        current_narration_lines: list[str] | None = None

        for line in script_markdown.splitlines():
            normalized_line = line.strip()
            label, separator, value = normalized_line.partition(":")

            if separator and label.strip().lower() == "narration":
                current_narration_lines = [value.strip()]
                continue

            if current_narration_lines is not None and self._ends_narration_block(
                normalized_line
            ):
                self._append_segment(segments, current_narration_lines)
                current_narration_lines = None

            if current_narration_lines is not None:
                current_narration_lines.append(normalized_line)

        if current_narration_lines is not None:
            self._append_segment(segments, current_narration_lines)

        if not segments:
            raise VoiceoverNarrationError(
                "Approved script contains no Narration lines."
            )

        return segments

    def _append_segment(
        self, segments: list[VoiceoverSegment], narration_lines: list[str]
    ) -> None:
        order = len(segments) + 1
        narration_text = "\n".join(
            line for line in self._trim_blank_edges(narration_lines) if line
        ).strip()
        if not narration_text:
            raise VoiceoverNarrationError(f"Narration line {order} is blank.")
        segments.append(
            VoiceoverSegment(
                segment_id=f"segment-{order:03d}",
                order=order,
                narration_text=narration_text,
            )
        )

    def _trim_blank_edges(self, lines: list[str]) -> list[str]:
        start = 0
        end = len(lines)
        while start < end and not lines[start]:
            start += 1
        while end > start and not lines[end - 1]:
            end -= 1
        return lines[start:end]

    def _ends_narration_block(self, line: str) -> bool:
        if line.startswith("#"):
            return True
        label, separator, _ = line.partition(":")
        return bool(separator and label.strip().lower() in {
            "on-screen text",
            "purpose",
            "facts used",
            "source",
            "claim",
        })
