import wave
from pathlib import Path

import pytest

from hyperframevideo.vieneu_voiceover import (
    VieNeuVoiceoverProvider,
    VoiceoverProviderError,
)
from hyperframevideo.voiceover_segments import VoiceoverSegment


class FakeVieNeuTts:
    def __init__(self) -> None:
        self.inferred_texts: list[str] = []
        self.inferred_voices: list[object] = []
        self.saved_paths: list[Path] = []
        self.requested_voice_names: list[str] = []
        self.closed = False

    def infer(self, *, text: str, voice=None):
        self.inferred_texts.append(text)
        self.inferred_voices.append(voice)
        return text.encode("utf-8")

    def get_preset_voice(self, voice_name: str):
        self.requested_voice_names.append(voice_name)
        return {"voice_id": voice_name}

    def save(self, audio, path: str) -> None:
        output_path = Path(path)
        self.saved_paths.append(output_path)
        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(8000)
            wav_file.writeframes(b"\0\0" * 8000)

    def close(self) -> None:
        self.closed = True


def test_vieneu_provider_writes_one_wav_per_ordered_segment(tmp_path: Path) -> None:
    fake_tts = FakeVieNeuTts()
    provider = VieNeuVoiceoverProvider(sdk_factory=lambda **kwargs: fake_tts)
    segments = [
        VoiceoverSegment(
            segment_id="segment-001",
            order=1,
            narration_text="First narration.",
        ),
        VoiceoverSegment(
            segment_id="segment-002",
            order=2,
            narration_text="Second narration.",
        ),
    ]

    outputs = provider.synthesize(segments, audio_dir=tmp_path)

    assert fake_tts.inferred_texts == ["First narration.", "Second narration."]
    assert fake_tts.saved_paths == [
        tmp_path / "segment-001.wav",
        tmp_path / "segment-002.wav",
    ]
    assert fake_tts.closed is True
    assert [output.segment_id for output in outputs] == ["segment-001", "segment-002"]
    assert [output.audio_path for output in outputs] == fake_tts.saved_paths
    assert [output.duration_seconds for output in outputs] == [1.0, 1.0]


def test_vieneu_provider_records_selected_voice_configuration(
    tmp_path: Path,
) -> None:
    fake_tts = FakeVieNeuTts()
    provider = VieNeuVoiceoverProvider(
        sdk_factory=lambda **kwargs: fake_tts,
        mode="standard",
        voice_name="female_north",
    )

    outputs = provider.synthesize(
        [
            VoiceoverSegment(
                segment_id="segment-001",
                order=1,
                narration_text="Xin chao.",
            )
        ],
        audio_dir=tmp_path,
    )

    assert fake_tts.requested_voice_names == ["female_north"]
    assert fake_tts.inferred_voices == [{"voice_id": "female_north"}]
    assert outputs[0].provider_name == "vieneu"
    assert outputs[0].voice_config == {
        "mode": "standard",
        "voice_name": "female_north",
    }


def test_vieneu_provider_reports_missing_sdk_readably(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import builtins

    original_import = builtins.__import__

    def reject_vieneu(name, *args, **kwargs):
        if name == "vieneu":
            raise ImportError("No module named 'vieneu'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject_vieneu)
    provider = VieNeuVoiceoverProvider()

    with pytest.raises(VoiceoverProviderError) as error:
        provider.synthesize(
            [
                VoiceoverSegment(
                    segment_id="segment-001",
                    order=1,
                    narration_text="Xin chao.",
                )
            ],
            audio_dir=tmp_path,
        )

    assert "VieNeu SDK is not installed" in str(error.value)


def test_vieneu_provider_reports_runtime_setup_failure_readably(tmp_path: Path) -> None:
    def failing_factory(**kwargs):
        raise RuntimeError("model cache is unavailable")

    provider = VieNeuVoiceoverProvider(sdk_factory=failing_factory)

    with pytest.raises(VoiceoverProviderError) as error:
        provider.synthesize(
            [
                VoiceoverSegment(
                    segment_id="segment-001",
                    order=1,
                    narration_text="Xin chao.",
                )
            ],
            audio_dir=tmp_path,
        )

    assert str(error.value) == (
        "VieNeu voiceover runtime setup failed: model cache is unavailable"
    )
