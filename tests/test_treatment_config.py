import json
from pathlib import Path

import pytest

from hyperframevideo.treatment_config import (
    TreatmentConfig,
    TreatmentConfigError,
    TreatmentConfigLoader,
)


class TestTreatmentConfigLoader:
    """A typed loader reads treatments.json and returns TreatmentConfig by name."""

    def test_loads_known_treatment(self, tmp_path: Path) -> None:
        config_path = tmp_path / "treatments.json"
        config_path.write_text(
            json.dumps({
                "treatments": [
                    {
                        "name": "ai-modern",
                        "background_color": "#0f172a",
                        "text_color": "#f8fafc",
                        "accent_color": "#3b82f6",
                        "font_family": "Inter, sans-serif",
                        "title_font_size": "48px",
                        "body_font_size": "24px",
                        "fade_in_duration": 0.5,
                        "slide_up_duration": 0.6,
                    },
                ],
            }),
            encoding="utf-8",
        )

        result = TreatmentConfigLoader().load(config_path, "ai-modern")

        assert isinstance(result, TreatmentConfig)
        assert result.name == "ai-modern"
        assert result.background_color == "#0f172a"
        assert result.text_color == "#f8fafc"
        assert result.accent_color == "#3b82f6"
        assert result.font_family == "Inter, sans-serif"
        assert result.title_font_size == "48px"
        assert result.body_font_size == "24px"
        assert result.fade_in_duration == 0.5
        assert result.slide_up_duration == 0.6

    def test_unknown_treatment_raises_diagnostic(self, tmp_path: Path) -> None:
        config_path = tmp_path / "treatments.json"
        config_path.write_text(
            json.dumps({"treatments": [{"name": "ai-modern", "background_color": "#000", "text_color": "#fff", "accent_color": "#00f", "font_family": "sans-serif", "title_font_size": "48px", "body_font_size": "24px", "fade_in_duration": 0.5, "slide_up_duration": 0.6}]}),
            encoding="utf-8",
        )

        with pytest.raises(TreatmentConfigError) as error:
            TreatmentConfigLoader().load(config_path, "cinematic-dark")

        assert "Unknown treatment" in str(error.value)

    def test_malformed_json_raises_diagnostic(self, tmp_path: Path) -> None:
        config_path = tmp_path / "broken.json"
        config_path.write_text("not valid json", encoding="utf-8")

        with pytest.raises(TreatmentConfigError) as error:
            TreatmentConfigLoader().load(config_path, "ai-modern")

        assert "Invalid treatment config" in str(error.value)

    def test_missing_treatments_key_raises_diagnostic(self, tmp_path: Path) -> None:
        config_path = tmp_path / "treatments.json"
        config_path.write_text("{}", encoding="utf-8")

        with pytest.raises(TreatmentConfigError) as error:
            TreatmentConfigLoader().load(config_path, "ai-modern")

        assert "missing treatments" in str(error.value)

    def test_missing_config_file_raises_diagnostic(self, tmp_path: Path) -> None:
        config_path = tmp_path / "nonexistent.json"

        with pytest.raises(TreatmentConfigError) as error:
            TreatmentConfigLoader().load(config_path, "ai-modern")

        assert "Treatment config not found" in str(error.value)

    def test_loads_and_matches_default_treatments_json(self) -> None:
        from hyperframevideo import treatment_config as tc

        config_path = Path(tc.__file__).parent / "treatments.json"

        result = TreatmentConfigLoader().load(config_path, "ai-modern")

        assert result.name == "ai-modern"
        assert result.background_color
        assert result.text_color
        assert result.fade_in_duration > 0

    def test_secondary_color_defaults_to_empty_string(self) -> None:
        """secondary_color is optional; defaults to empty for backward compat."""
        treatment = TreatmentConfig(
            name="ai-modern",
            background_color="#000",
            text_color="#fff",
            accent_color="#00f",
            font_family="sans-serif",
            title_font_size="48px",
            body_font_size="24px",
            fade_in_duration=0.5,
            slide_up_duration=0.6,
        )
        assert treatment.secondary_color == ""

    def test_secondary_color_from_json(self, tmp_path: Path) -> None:
        config_path = tmp_path / "treatments.json"
        config_path.write_text(
            json.dumps({
                "treatments": [
                    {
                        "name": "tech-hype",
                        "background_color": "#0d0221",
                        "text_color": "#ffffff",
                        "accent_color": "#ff6b6b",
                        "secondary_color": "#ffd93d",
                        "font_family": "Inter, sans-serif",
                        "title_font_size": "56px",
                        "body_font_size": "32px",
                        "fade_in_duration": 0.2,
                        "slide_up_duration": 0.3,
                    },
                ],
            }),
            encoding="utf-8",
        )

        result = TreatmentConfigLoader().load(config_path, "tech-hype")

        assert result.name == "tech-hype"
        assert result.secondary_color == "#ffd93d"
        assert result.accent_color == "#ff6b6b"
        assert result.background_color == "#0d0221"
