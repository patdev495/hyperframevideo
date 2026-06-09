from __future__ import annotations

import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol, Sequence

from hyperframevideo.voiceover_segments import VoiceoverSegment


class VoiceoverProvider(Protocol):
    def synthesize(
        self, segments: Sequence[VoiceoverSegment], audio_dir: Path
    ) -> list["VoiceoverOutput"]:
        pass


class VoiceoverProviderError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class VoiceoverOutput:
    segment_id: str
    order: int
    narration_text: str
    audio_path: Path
    duration_seconds: float
    provider_name: str
    voice_config: dict[str, str]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class VieNeuVoiceoverProvider:
    sdk_factory: Callable[..., Any] | None = None
    mode: str = "standard"
    voice_name: str | None = None
    provider_name: str = "vieneu"
    sdk_options: dict[str, Any] = field(default_factory=dict)

    def synthesize(
        self, segments: Sequence[VoiceoverSegment], audio_dir: Path
    ) -> list[VoiceoverOutput]:
        audio_dir.mkdir(parents=True, exist_ok=True)
        tts = self._create_tts()
        voice = None
        if self.voice_name is not None:
            voice = tts.get_preset_voice(self.voice_name)

        outputs: list[VoiceoverOutput] = []
        try:
            for segment in segments:
                audio_path = audio_dir / f"{segment.segment_id}.wav"
                if voice is None:
                    audio = tts.infer(text=segment.narration_text)
                else:
                    audio = tts.infer(text=segment.narration_text, voice=voice)
                tts.save(audio, str(audio_path))
                outputs.append(
                    VoiceoverOutput(
                        segment_id=segment.segment_id,
                        order=segment.order,
                        narration_text=segment.narration_text,
                        audio_path=audio_path,
                        duration_seconds=self._wav_duration_seconds(audio_path),
                        provider_name=self.provider_name,
                        voice_config=self._voice_config(),
                    )
                )
        finally:
            close = getattr(tts, "close", None)
            if close is not None:
                close()

        return outputs

    def _create_tts(self) -> Any:
        if self.sdk_factory is not None:
            try:
                return self.sdk_factory(mode=self.mode, **self.sdk_options)
            except VoiceoverProviderError:
                raise
            except Exception as error:
                raise VoiceoverProviderError(
                    f"VieNeu voiceover runtime setup failed: {error}"
                ) from error

        try:
            from vieneu import Vieneu
        except ImportError as error:
            raise VoiceoverProviderError(
                "VieNeu SDK is not installed. Install the optional VieNeu runtime before generating voiceover."
            ) from error

        try:
            return Vieneu(mode=self.mode, **self.sdk_options)
        except Exception as error:
            raise VoiceoverProviderError(
                f"VieNeu voiceover runtime setup failed: {error}"
            ) from error

    def _voice_config(self) -> dict[str, str]:
        return {
            "mode": self.mode,
            "voice_name": self.voice_name or "default",
        }

    def _wav_duration_seconds(self, audio_path: Path) -> float:
        with wave.open(str(audio_path), "rb") as wav_file:
            frames = wav_file.getnframes()
            framerate = wav_file.getframerate()
        return frames / framerate
