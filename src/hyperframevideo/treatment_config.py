from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class TreatmentConfigError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class TreatmentConfig:
    name: str
    background_color: str
    text_color: str
    accent_color: str
    font_family: str
    title_font_size: str
    body_font_size: str
    fade_in_duration: float
    slide_up_duration: float


@dataclass(frozen=True, slots=True)
class TreatmentConfigLoader:

    def load(self, config_path: Path, treatment_name: str) -> TreatmentConfig:
        try:
            payload = json.loads(config_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise TreatmentConfigError(
                f"Treatment config not found: {config_path}"
            ) from error
        except json.JSONDecodeError as error:
            raise TreatmentConfigError(
                f"Invalid treatment config JSON: {error.msg}."
            ) from error

        treatments = payload.get("treatments")
        if not isinstance(treatments, list):
            raise TreatmentConfigError(
                "Treatment config is missing treatments list."
            )

        for entry in treatments:
            if not isinstance(entry, dict):
                raise TreatmentConfigError(
                    "Each treatment must be a JSON object."
                )
            if entry.get("name") == treatment_name:
                return self._build(entry)

        raise TreatmentConfigError(
            f"Unknown treatment: {treatment_name!r}."
        )

    def _build(self, entry: dict[str, Any]) -> TreatmentConfig:
        try:
            return TreatmentConfig(
                name=str(entry["name"]),
                background_color=str(entry["background_color"]),
                text_color=str(entry["text_color"]),
                accent_color=str(entry["accent_color"]),
                font_family=str(entry["font_family"]),
                title_font_size=str(entry["title_font_size"]),
                body_font_size=str(entry["body_font_size"]),
                fade_in_duration=float(entry["fade_in_duration"]),
                slide_up_duration=float(entry["slide_up_duration"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            raise TreatmentConfigError(
                f"Invalid treatment entry: {error}."
            ) from error
