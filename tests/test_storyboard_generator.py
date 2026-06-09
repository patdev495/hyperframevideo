from hyperframevideo.storyboard_planning import StoryboardScene
from hyperframevideo.storyboard_generator import StoryboardMarkdownGenerator


class TestStoryboardMarkdownGenerator:
    """STORYBOARD.md content is deterministic and includes header + one scene per entry."""

    def test_generates_header_and_one_scene(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=1.5,
                audio_path="voiceover/segment-001.wav",
                narration_text="First scene narration.",
                on_screen_text="First screen text.",
                purpose="Introduce the topic.",
                facts_used="Fact A about the topic.",
            ),
        ]

        result = StoryboardMarkdownGenerator().generate(
            scenes,
            run_id="run-001",
            visual_treatment="ai-modern",
        )

        assert result.startswith("# Storyboard")
        assert "Run ID: run-001" in result
        assert "Visual Treatment: ai-modern" in result
        assert "Total Duration: 1.50s" in result
        assert "Source Artifacts: SCRIPT.md, voiceover.json" in result

        assert "## Scene 1" in result
        assert "**Segment ID:** segment-001" in result
        assert "**Order:** 1" in result
        assert "**Start Time:** 0.00s" in result
        assert "**Duration:** 1.50s" in result
        assert "**Audio:** voiceover/segment-001.wav" in result
        assert "**Narration:** First scene narration." in result
        assert "**On-screen Text:** First screen text." in result
        assert "**Purpose:** Introduce the topic." in result
        assert "**Facts Used:** Fact A about the topic." in result
        assert "**Visual Direction:** [ai-modern]" in result

    def test_multiple_scenes_with_cumulative_header(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=1.5,
                audio_path="voiceover/segment-001.wav",
                narration_text="First.",
                on_screen_text="Screen one.",
                purpose="Intro.",
                facts_used="Fact 1.",
            ),
            StoryboardScene(
                order=2,
                segment_id="segment-002",
                start_time_seconds=1.5,
                duration_seconds=2.0,
                audio_path="voiceover/segment-002.wav",
                narration_text="Second.",
                on_screen_text="Screen two.",
                purpose="Body.",
                facts_used="Fact 2.",
            ),
        ]

        result = StoryboardMarkdownGenerator().generate(scenes, run_id="run-X")

        assert "Run ID: run-X" in result
        assert "Total Duration: 3.50s" in result

        assert "## Scene 1" in result
        assert "**Start Time:** 0.00s" in result
        assert "**Duration:** 1.50s" in result
        assert "**Narration:** First." in result

        assert "## Scene 2" in result
        assert "**Start Time:** 1.50s" in result
        assert "**Duration:** 2.00s" in result
        assert "**Narration:** Second." in result

    def test_custom_visual_treatment(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=1.0,
                audio_path="voiceover/segment-001.wav",
                narration_text="Narration.",
                on_screen_text="Screen.",
                purpose=None,
                facts_used=None,
            ),
        ]

        result = StoryboardMarkdownGenerator().generate(
            scenes, run_id="run-001", visual_treatment="cinematic-dark"
        )

        assert "Visual Treatment: cinematic-dark" in result
        assert "**Visual Direction:** [cinematic-dark]" in result

    def test_empty_scenes_list(self) -> None:
        result = StoryboardMarkdownGenerator().generate(
            [], run_id="run-empty", visual_treatment="ai-modern"
        )

        assert result.startswith("# Storyboard")
        assert "Run ID: run-empty" in result
        assert "Total Duration: 0.00s" in result
        assert "## Scene" not in result

    def test_deterministic_output(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=1.0,
                audio_path="voiceover/segment-001.wav",
                narration_text="Narration.",
                on_screen_text="Screen.",
                purpose="Purpose.",
                facts_used="Facts.",
            ),
        ]

        gen = StoryboardMarkdownGenerator()
        result1 = gen.generate(scenes, run_id="run-001")
        result2 = gen.generate(scenes, run_id="run-001")

        assert result1 == result2

    def test_default_run_id_is_empty_string(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=1.0,
                audio_path="voiceover/segment-001.wav",
                narration_text="Narration.",
                on_screen_text="Screen.",
                purpose=None,
                facts_used=None,
            ),
        ]

        result = StoryboardMarkdownGenerator().generate(scenes)

        assert "Run ID: " in result
