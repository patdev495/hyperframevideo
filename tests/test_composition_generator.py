from hyperframevideo.storyboard_planning import StoryboardScene
from hyperframevideo.treatment_config import TreatmentConfig
from hyperframevideo.composition_generator import CompositionGenerator
from hyperframevideo.karaoke_captions import (
    KaraokeCaptionManifest,
    KaraokeCaptionSegment,
    KaraokeCaptionToken,
)


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
        assert 'class="clip scene"' in result
        assert 'data-start="0.0"' in result or 'data-start="0"' in result
        assert 'data-duration="1.5"' in result
        assert 'data-track-index="0"' in result
        # Content
        assert "First narration." in result
        assert "First screen." in result
        # Audio
        assert 'id="audio-segment-001"' in result
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

    def test_premium_news_generates_background_transitions_and_karaoke_captions(self) -> None:
        scenes = [
            StoryboardScene(
                order=1,
                segment_id="segment-001",
                start_time_seconds=0.0,
                duration_seconds=2.0,
                audio_path="voiceover/segment-001.wav",
                narration_text="OpenAI builds ChatGPT.",
                on_screen_text="ChatGPT Super App",
                purpose="Hook",
                facts_used=None,
            ),
        ]
        treatment = TreatmentConfig(
            name="premium-news",
            background_color="#050816",
            text_color="#f8fafc",
            accent_color="#38bdf8",
            font_family="Inter, sans-serif",
            title_font_size="72px",
            body_font_size="38px",
            fade_in_duration=0.45,
            slide_up_duration=0.7,
        )
        captions = KaraokeCaptionManifest(
            timing_source="test-double",
            segments=(
                KaraokeCaptionSegment(
                    segment_id="segment-001",
                    tokens=(
                        KaraokeCaptionToken(
                            order=1,
                            text="OpenAI",
                            start_seconds=0.0,
                            end_seconds=0.6,
                        ),
                        KaraokeCaptionToken(
                            order=2,
                            text="builds",
                            start_seconds=0.6,
                            end_seconds=1.2,
                        ),
                        KaraokeCaptionToken(
                            order=3,
                            text="ChatGPT",
                            start_seconds=1.2,
                            end_seconds=2.0,
                        ),
                    ),
                ),
            ),
        )

        result = CompositionGenerator().generate(
            scenes,
            treatment,
            run_id="premium-run",
            karaoke_captions=captions,
        )

        assert 'data-visual-treatment="premium-news"' in result
        assert 'class="clip scene premium-scene"' in result
        assert "premium-bg-layer" in result
        assert "premium-transition" in result
        assert "karaoke-caption" in result
        assert "caption-window" in result
        assert "active-word" in result
        assert "tl.set" in result
        assert 'data-token-start="1.2"' in result
        assert 'data-token-end="2.0"' in result
        assert "OpenAI builds ChatGPT." not in result
        assert '<audio id="audio-segment-001" data-start="0.0" data-duration="2.0" data-track-index="1"' in result
        assert "window.__timelines" in result
        assert 'tl.set(".scene:nth-of-type(1) [data-token-order=\'1\']"' in result

    def test_tech_hype_generates_split_text_kaboom_and_background_layers(self) -> None:
        """tech-hype treatment produces HTML with particle bg, scanlines,
        split-word text animation, cycled transitions, data callouts."""
        scenes = [
            StoryboardScene(
                order=1, segment_id="seg-001", start_time_seconds=0.0,
                duration_seconds=2.0, audio_path="voice.wav",
                narration_text="First scene with 340% growth.",
                on_screen_text="Tech News Today",
                purpose="Hook", facts_used=None,
            ),
            StoryboardScene(
                order=2, segment_id="seg-002", start_time_seconds=2.0,
                duration_seconds=2.0, audio_path="voice2.wav",
                narration_text="Second scene here.",
                on_screen_text="Market Update",
                purpose="Body", facts_used=None,
            ),
        ]
        treatment = TreatmentConfig(
            name="tech-hype",
            background_color="#0d0221",
            text_color="#ffffff",
            accent_color="#ff6b6b",
            secondary_color="#ffd93d",
            font_family="Inter, sans-serif",
            title_font_size="56px",
            body_font_size="32px",
            fade_in_duration=0.2,
            slide_up_duration=0.35,
        )

        result = CompositionGenerator().generate(scenes, treatment, run_id="tech-run")

        # Dispatches to tech-hype template
        assert "tech-hype" in result or "data-visual-treatment=" in result
        # Background layers
        assert "scanlines" in result
        assert "particle" in result.lower() or "particle" in result
        # Split-word animation: each word in its own span
        assert "split-word" in result
        # GSAP stagger for split text
        assert "stagger" in result
        # Scene transition styles (slide, zoom, glitch)
        assert "slide" in result.lower() or "glitch" in result.lower() or "zoom" in result.lower()
        # Data callout glow on number
        assert "data-glow" in result or "data-callout" in result or "340" in result
        # Deterministic
        result2 = CompositionGenerator().generate(scenes, treatment, run_id="tech-run")
        assert result == result2
