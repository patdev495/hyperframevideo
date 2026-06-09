from __future__ import annotations

import re
from dataclasses import dataclass

from hyperframevideo.markdown_fields import partition_markdown_field


class ScriptStoryboardError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class ScriptScene:
    segment_id: str
    order: int
    narration_text: str
    on_screen_text: str | None
    purpose: str | None
    facts_used: str | None


@dataclass(frozen=True, slots=True)
class ScriptStoryboardExtractor:

    _FIELD_LABELS: tuple[tuple[str, str], ...] = (
        ("narration", "narration_text"),
        ("on-screen text", "on_screen_text"),
        ("purpose", "purpose"),
        ("facts used", "facts_used"),
    )

    def extract(self, script_markdown: str) -> list[ScriptScene]:
        segment_blocks = self._split_segments(script_markdown)
        if not segment_blocks:
            raise ScriptStoryboardError("No segments found in script.")
        scenes: list[ScriptScene] = []
        for order, block in enumerate(segment_blocks, start=1):
            scene = self._parse_segment(block, order)
            scenes.append(scene)
        return scenes

    def _split_segments(self, script_markdown: str) -> list[str]:
        parts = re.split(r"^## Segment \d+", script_markdown, flags=re.MULTILINE)
        # First part is content before any ## Segment (header, status, etc.)
        return [part.strip() for part in parts[1:] if part.strip()]

    def _parse_segment(self, block: str, order: int) -> ScriptScene:
        field_values: dict[str, str | None] = {
            "narration_text": None,
            "on_screen_text": None,
            "purpose": None,
            "facts_used": None,
        }
        current_field: str | None = None
        current_lines: list[str] = []

        for line in block.splitlines():
            normalized = line.strip()
            if not normalized:
                if current_field is not None:
                    current_lines.append("")
                continue

            matched_field = self._match_field_label(normalized)
            if matched_field is not None:
                # Flush previous field
                if current_field is not None:
                    field_values[current_field] = self._join_lines(current_lines)
                current_field = matched_field
                _, separator, value = partition_markdown_field(normalized)
                current_lines = [value.strip()] if value.strip() else []
            elif current_field is not None:
                current_lines.append(normalized)

        # Flush last field
        if current_field is not None:
            field_values[current_field] = self._join_lines(current_lines)

        # Validate required fields
        if not field_values["narration_text"]:
            raise ScriptStoryboardError(
                f"Segment {order} is missing Narration."
            )
        if not field_values["on_screen_text"]:
            raise ScriptStoryboardError(
                f"Segment {order} is missing On-screen text."
            )

        return ScriptScene(
            segment_id=f"segment-{order:03d}",
            order=order,
            narration_text=field_values["narration_text"],
            on_screen_text=field_values["on_screen_text"],
            purpose=field_values["purpose"],
            facts_used=field_values["facts_used"],
        )

    def _match_field_label(self, line: str) -> str | None:
        """Return the attr name if line starts with a known field label."""
        label_text, separator, _ = partition_markdown_field(line)
        if not separator:
            return None
        for label, attr in self._FIELD_LABELS:
            if label_text.strip().lower() == label:
                return attr
        return None

    def _join_lines(self, lines: list[str]) -> str | None:
        text = "\n".join(lines).strip()
        return text if text else None
