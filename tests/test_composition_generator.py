from hyperframevideo.storyboard_planning import StoryboardScene
from hyperframevideo.treatment_config import TreatmentConfig
from hyperframevideo.composition_generator import CompositionGenerator


class TestCompositionGenerator:
    """Generate valid HyperFrames HTML from StoryboardScene list + TreatmentConfig."""

    def test_generates_html_with_stage_and_scenes(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=1.5,
                audio_path="voiceover/segment-001.wav",
                narration_text="First narration.",
                on_screen_text="First screen.",
                purpose="Intro.",
                facts_used="Fact 1.",
            ),
        ]
        treatment = TreatmentConfig(
            name="ai-modern",
            background_color="#0f172a",
            text_color="#f8fafc",
            accent_color="#3b82f6",
            font_family="Inter, sans-serif",
            title_font_size="48px",
            body_font_size="24px",
            fade_in_duration=0.5,
            slide_up_duration=0.6,
        )

        result = CompositionGenerator().generate(
            scenes, treatment, run_id="run-001"
        )

        assert "<!DOCTYPE html>" in result
        assert '<div id="stage"' in result
        assert 'data-composition-id="run-001"' in result
        assert 'data-width="1080"' in result
        assert 'data-height="1920"' in result
        # Scene with data attributes
        assert 'data-start="0.0"' in result or 'data-start="0"' in result
        assert 'data-duration="1.5"' in result
        assert 'data-track-index="0"' in result
        # Content
        assert "First narration." in result
        assert "First screen." in result
        # Audio
        assert "voiceover/segment-001.wav" in result
        # Treatment CSS
        assert "#0f172a" in result
        assert "#f8fafc" in result
        assert "#3b82f6" in result
        assert "Inter, sans-serif" in result
        assert "48px" in result
        assert "24px" in result
        # GSAP
        assert "gsap" in result or "GSAP" in result
        assert "timeline" in result
        # Deterministic
        result2 = CompositionGenerator().generate(
            scenes, treatment, run_id="run-001"
        )
        assert result == result2


    def test_multiple_scenes_have_sequential_timing_and_tracks(self) -> None:
        scenes = [
            StoryboardScene(
                order=1, segment_id="segment-001", start_time_seconds=0.0,
                duration_seconds=1.5, audio_path="voiceover/segment-001.wav",
                narration_text="First.", on_screen_text="S1",
                purpose=None, facts_used=None,
            ),
            StoryboardScene(
                order=2, segment_id="segment-002", start_time_seconds=1.5,
                duration_seconds=2.0, audio_path="voiceover/segment-002.wav",
                narration_text="Second.", on_screen_text="S2",
                purpose=None, facts_used=None,
            ),
        ]
        treatment = TreatmentConfig(
            name="ai-modern", background_color="#000", text_color="#fff",
            accent_color="#00f", font_family="sans-serif",
            title_font_size="48px", body_font_size="24px",
            fade_in_duration=0.5, slide_up_duration=0.6,
        )

        result = CompositionGenerator().generate(scenes, treatment, run_id="run-X")

        assert 'data-start="0.0"' in result
        assert 'data-duration="1.5"' in result
        assert 'data-track-index="0"' in result
        assert 'data-start="1.5"' in result
        assert 'data-duration="2.0"' in result
        assert 'data-track-index="1"' in result
        assert "segment-001.wav" in result
        assert "segment-002.wav" in result
        assert "First." in result
        assert "Second." in result

    def test_empty_scenes_produces_minimal_html(self) -> None:
        treatment = TreatmentConfig(
            name="ai-modern", background_color="#000", text_color="#fff",
            accent_color="#00f", font_family="sans-serif",
            title_font_size="48px", body_font_size="24px",
            fade_in_duration=0.5, slide_up_duration=0.6,
        )

        result = CompositionGenerator().generate([], treatment, run_id="empty")

        assert "<!DOCTYPE html>" in result
        assert 'data-composition-id="empty"' in result
        assert "nth-child" not in result

    def test_custom_treatment_appears_in_css(self) -> None:
        scenes = [
            StoryboardScene(
                order=1, segment_id="segment-001", start_time_seconds=0.0,
                duration_seconds=1.0, audio_path="voice.wav",
                narration_text="Narration.", on_screen_text="Screen.",
                purpose=None, facts_used=None,
            ),
        ]
        treatment = TreatmentConfig(
            name="cinematic", background_color="#1a1a2e", text_color="#e94560",
            accent_color="#16213e", font_family="Georgia, serif",
            title_font_size="36px", body_font_size="18px",
            fade_in_duration=0.8, slide_up_duration=0.4,
        )

        result = CompositionGenerator().generate(scenes, treatment, run_id="custom")

        assert "#1a1a2e" in result
        assert "#e94560" in result
        assert "Georgia, serif" in result
        assert "36px" in result
        assert "18px" in result
        assert "opacity: 0, y: 40" in result

    def test_on_screen_text_none_omits_title(self) -> None:
        scenes = [
            StoryboardScene(
                order=1, segment_id="segment-001", start_time_seconds=0.0,
                duration_seconds=1.0, audio_path="voice.wav",
                narration_text="Only narration.", on_screen_text=None,
                purpose=None, facts_used=None,
            ),
        ]
        treatment = TreatmentConfig(
            name="ai-modern", background_color="#000", text_color="#fff",
            accent_color="#00f", font_family="sans-serif",
            title_font_size="48px", body_font_size="24px",
            fade_in_duration=0.5, slide_up_duration=0.6,
        )

        result = CompositionGenerator().generate(scenes, treatment, run_id="run")

        assert "Only narration." in result
        assert '<h2 class="title">' not in result
        assert '<p class="body">Only narration.</p>' in result
