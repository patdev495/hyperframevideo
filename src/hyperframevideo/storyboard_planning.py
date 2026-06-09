from __future__ import annotations

from dataclasses import dataclass

from hyperframevideo.script_scenes import ScriptScene
from hyperframevideo.voiceover_timing import VoiceoverTimingEntry


class StoryboardPlanningError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class StoryboardScene:
    order: int
    segment_id: str
    start_time_seconds: float
    duration_seconds: float
    audio_path: str
    narration_text: str
    on_screen_text: str | None
    purpose: str | None
    facts_used: str | None


@dataclass(frozen=True, slots=True)
class StoryboardPlanner:

    def plan(
        self,
        scenes: list[ScriptScene],
        timing: list[VoiceoverTimingEntry],
    ) -> list[StoryboardScene]:
        timing_by_id: dict[str, VoiceoverTimingEntry] = {}
        for entry in timing:
            if entry.segment_id in timing_by_id:
                raise StoryboardPlanningError(
                    f"Duplicate segment ID {entry.segment_id!r} in voiceover timing."
                )
            timing_by_id[entry.segment_id] = entry

        planned: list[StoryboardScene] = []
        current_time = 0.0

        for scene in sorted(scenes, key=lambda s: s.order):
            timing_entry = timing_by_id.get(scene.segment_id)
            if timing_entry is None:
                raise StoryboardPlanningError(
                    f"No voiceover timing entry for {scene.segment_id!r}."
                )

            if scene.narration_text != timing_entry.narration_text:
                raise StoryboardPlanningError(
                    f"Narration mismatch for {scene.segment_id!r}: "
                    f"script says {scene.narration_text!r} but voiceover says "
                    f"{timing_entry.narration_text!r}."
                )

            planned.append(
                StoryboardScene(
                    order=scene.order,
                    segment_id=scene.segment_id,
                    start_time_seconds=current_time,
                    duration_seconds=timing_entry.duration_seconds,
                    audio_path=timing_entry.audio_path,
                    narration_text=scene.narration_text,
                    on_screen_text=scene.on_screen_text,
                    purpose=scene.purpose,
                    facts_used=scene.facts_used,
                )
            )
            current_time += timing_entry.duration_seconds

        # Check for extra timing entries with no matching scene
        matched_ids = {scene.segment_id for scene in scenes}
        for entry in timing:
            if entry.segment_id not in matched_ids:
                raise StoryboardPlanningError(
                    f"No script scene for voiceover segment {entry.segment_id!r}."
                )

        return planned
