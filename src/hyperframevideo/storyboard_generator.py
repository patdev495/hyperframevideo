from __future__ import annotations

from dataclasses import dataclass

from hyperframevideo.storyboard_planning import StoryboardScene


@dataclass(frozen=True, slots=True)
class StoryboardMarkdownGenerator:
    _SOURCE_ARTIFACTS = "SCRIPT.md, voiceover.json"

    def generate(
        self,
        scenes: list[StoryboardScene],
        *,
        run_id: str = "",
        visual_treatment: str = "tech-hype",
    ) -> str:
        total_duration = sum(scene.duration_seconds for scene in scenes)
        lines: list[str] = ["# Storyboard", ""]

        lines.append(f"Run ID: {run_id}")
        lines.append(f"Visual Treatment: {visual_treatment}")
        lines.append(f"Total Duration: {total_duration:.2f}s")
        lines.append(f"Source Artifacts: {self._SOURCE_ARTIFACTS}")
        lines.append("")

        for scene in scenes:
            lines.append(f"## Scene {scene.order}")
            lines.append("")
            lines.append(f"- **Segment ID:** {scene.segment_id}")
            lines.append(f"- **Order:** {scene.order}")
            lines.append(f"- **Start Time:** {scene.start_time_seconds:.2f}s")
            lines.append(f"- **Duration:** {scene.duration_seconds:.2f}s")
            lines.append(f"- **Audio:** {scene.audio_path}")
            lines.append(f"- **Narration:** {scene.narration_text}")
            lines.append(f"- **On-screen Text:** {scene.on_screen_text or ''}")
            lines.append(f"- **Purpose:** {scene.purpose or ''}")
            lines.append(f"- **Facts Used:** {scene.facts_used or ''}")
            lines.append(f"- **Visual Direction:** [{visual_treatment}]")
            lines.append("")

        return "\n".join(lines)
