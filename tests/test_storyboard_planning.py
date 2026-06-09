import pytest

from hyperframevideo.script_scenes import ScriptScene
from hyperframevideo.voiceover_timing import VoiceoverTimingEntry
from hyperframevideo.storyboard_planning import (
    StoryboardPlanner,
    StoryboardPlanningError,
)


class TestStoryboardPlannerHappyPath:
    """Scenes align with voiceover timing by segment_id, producing correct cumulative start times."""

    def test_successful_alignment_with_cumulative_start_times(self) -> None:
        scenes = [
            ScriptScene(
                segment_id="segment-001",
                order=1,
                narration_text="First scene.",
                on_screen_text="First screen.",
                purpose="Introduce.",
                facts_used="Fact A.",
            ),
            ScriptScene(
                segment_id="segment-002",
                order=2,
                narration_text="Second scene.",
                on_screen_text="Second screen.",
                purpose="Develop.",
                facts_used="Fact B.",
            ),
            ScriptScene(
                segment_id="segment-003",
                order=3,
                narration_text="Third scene.",
                on_screen_text="Third screen.",
                purpose="Conclude.",
                facts_used="Fact C.",
            ),
        ]

        timing = [
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=1,
                narration_text="First scene.",
                audio_path="voiceover/segment-001.wav",
                duration_seconds=1.5,
            ),
            VoiceoverTimingEntry(
                segment_id="segment-002",
                order=2,
                narration_text="Second scene.",
                audio_path="voiceover/segment-002.wav",
                duration_seconds=2.0,
            ),
            VoiceoverTimingEntry(
                segment_id="segment-003",
                order=3,
                narration_text="Third scene.",
                audio_path="voiceover/segment-003.wav",
                duration_seconds=0.75,
            ),
        ]

        result = StoryboardPlanner().plan(scenes, timing)

        assert len(result) == 3

        # Scene 1
        assert result[0].order == 1
        assert result[0].segment_id == "segment-001"
        assert result[0].start_time_seconds == 0.0
        assert result[0].duration_seconds == 1.5
        assert result[0].audio_path == "voiceover/segment-001.wav"
        assert result[0].narration_text == "First scene."
        assert result[0].on_screen_text == "First screen."
        assert result[0].purpose == "Introduce."
        assert result[0].facts_used == "Fact A."

        # Scene 2
        assert result[1].order == 2
        assert result[1].segment_id == "segment-002"
        assert result[1].start_time_seconds == 1.5
        assert result[1].duration_seconds == 2.0
        assert result[1].audio_path == "voiceover/segment-002.wav"
        assert result[1].narration_text == "Second scene."
        assert result[1].on_screen_text == "Second screen."
        assert result[1].purpose == "Develop."
        assert result[1].facts_used == "Fact B."

        # Scene 3
        assert result[2].order == 3
        assert result[2].segment_id == "segment-003"
        assert result[2].start_time_seconds == 3.5  # 1.5 + 2.0
        assert result[2].duration_seconds == 0.75
        assert result[2].audio_path == "voiceover/segment-003.wav"
        assert result[2].narration_text == "Third scene."
        assert result[2].on_screen_text == "Third screen."
        assert result[2].purpose == "Conclude."
        assert result[2].facts_used == "Fact C."

    def test_successful_alignment_with_optional_fields_none(self) -> None:
        """On-screen text, purpose, and facts_used may all be None."""
        scenes = [
            ScriptScene(
                segment_id="segment-001",
                order=1,
                narration_text="Only narration.",
                on_screen_text="Screen.",
                purpose=None,
                facts_used=None,
            ),
        ]
        timing = [
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=1,
                narration_text="Only narration.",
                audio_path="voiceover/segment-001.wav",
                duration_seconds=1.0,
            ),
        ]

        result = StoryboardPlanner().plan(scenes, timing)

        assert len(result) == 1
        assert result[0].on_screen_text == "Screen."
        assert result[0].purpose is None
        assert result[0].facts_used is None


class TestStoryboardPlannerDiagnostics:
    """Missing, extra, duplicate, and mismatched entries produce readable diagnostics."""

    def test_missing_timing_entry(self) -> None:
        scenes = [
            ScriptScene(
                segment_id="segment-001",
                order=1,
                narration_text="Scene one.",
                on_screen_text="Screen one.",
                purpose=None,
                facts_used=None,
            ),
            ScriptScene(
                segment_id="segment-002",
                order=2,
                narration_text="Scene two.",
                on_screen_text="Screen two.",
                purpose=None,
                facts_used=None,
            ),
        ]
        timing = [
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=1,
                narration_text="Scene one.",
                audio_path="voiceover/segment-001.wav",
                duration_seconds=1.0,
            ),
            # segment-002 timing is missing
        ]

        with pytest.raises(StoryboardPlanningError) as error:
            StoryboardPlanner().plan(scenes, timing)

        assert "segment-002" in str(error.value)

    def test_extra_timing_entry(self) -> None:
        scenes = [
            ScriptScene(
                segment_id="segment-001",
                order=1,
                narration_text="Only scene.",
                on_screen_text="Screen.",
                purpose=None,
                facts_used=None,
            ),
        ]
        timing = [
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=1,
                narration_text="Only scene.",
                audio_path="voiceover/segment-001.wav",
                duration_seconds=1.0,
            ),
            VoiceoverTimingEntry(
                segment_id="segment-002",
                order=2,
                narration_text="Extra scene.",
                audio_path="voiceover/segment-002.wav",
                duration_seconds=0.5,
            ),
        ]

        with pytest.raises(StoryboardPlanningError) as error:
            StoryboardPlanner().plan(scenes, timing)

        assert "segment-002" in str(error.value)
        assert "No script scene" in str(error.value)

    def test_mismatched_narration_text(self) -> None:
        scenes = [
            ScriptScene(
                segment_id="segment-001",
                order=1,
                narration_text="Original script text.",
                on_screen_text="Screen.",
                purpose=None,
                facts_used=None,
            ),
        ]
        timing = [
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=1,
                narration_text="Different voiceover text.",
                audio_path="voiceover/segment-001.wav",
                duration_seconds=1.0,
            ),
        ]

        with pytest.raises(StoryboardPlanningError) as error:
            StoryboardPlanner().plan(scenes, timing)

        assert "Narration mismatch" in str(error.value)
        assert "segment-001" in str(error.value)

    def test_duplicate_segment_id_in_timing(self) -> None:
        scenes = [
            ScriptScene(
                segment_id="segment-001",
                order=1,
                narration_text="The scene.",
                on_screen_text="Screen.",
                purpose=None,
                facts_used=None,
            ),
        ]
        timing = [
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=1,
                narration_text="The scene.",
                audio_path="voiceover/segment-001.wav",
                duration_seconds=1.0,
            ),
            VoiceoverTimingEntry(
                segment_id="segment-001",
                order=2,
                narration_text="The scene.",
                audio_path="voiceover/segment-001-alt.wav",
                duration_seconds=1.5,
            ),
        ]

        with pytest.raises(StoryboardPlanningError) as error:
            StoryboardPlanner().plan(scenes, timing)

        assert "Duplicate" in str(error.value)
        assert "segment-001" in str(error.value)
