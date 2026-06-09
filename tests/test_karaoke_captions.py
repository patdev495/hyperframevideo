import pytest

from hyperframevideo.karaoke_captions import (
    ApproximateKaraokeCaptionProvider,
    CaptionTimingProvider,
    KaraokeCaptionError,
    KaraokeCaptionLoader,
    KaraokeCaptionManifest,
    KaraokeCaptionSegment,
    KaraokeCaptionToken,
)


def test_karaoke_caption_manifest_round_trips_segment_relative_tokens() -> None:
    manifest = KaraokeCaptionManifest(
        timing_source="approximate",
        segments=(
            KaraokeCaptionSegment(
                segment_id="segment-001",
                tokens=(
                    KaraokeCaptionToken(
                        order=1,
                        text="OpenAI",
                        start_seconds=0.0,
                        end_seconds=0.42,
                    ),
                    KaraokeCaptionToken(
                        order=2,
                        text="\u0111ang",
                        start_seconds=0.42,
                        end_seconds=0.68,
                    ),
                    KaraokeCaptionToken(
                        order=3,
                        text="chu\u1ea9n",
                        start_seconds=0.68,
                        end_seconds=0.95,
                    ),
                ),
            ),
        ),
    )

    loaded = KaraokeCaptionLoader().load(manifest.to_json())

    assert loaded == manifest
    assert loaded.segments[0].tokens[0].start_seconds == 0.0
    assert loaded.segments[0].tokens[0].end_seconds == 0.42
    assert loaded.segments[0].phrase_windows(max_tokens=2) == (
        (manifest.segments[0].tokens[0], manifest.segments[0].tokens[1]),
        (manifest.segments[0].tokens[2],),
    )


@pytest.mark.parametrize(
    ("tokens", "diagnostic"),
    [
        (
            [
                {"order": 1, "text": "bad", "start_seconds": -0.1, "end_seconds": 0.2},
            ],
            "must be segment-relative",
        ),
        (
            [
                {"order": 1, "text": "bad", "start_seconds": 0.5, "end_seconds": 0.5},
            ],
            "end_seconds must be greater than start_seconds",
        ),
        (
            [
                {"order": 1, "text": "first", "start_seconds": 0.0, "end_seconds": 0.7},
                {"order": 2, "text": "overlap", "start_seconds": 0.6, "end_seconds": 1.0},
            ],
            "must not overlap",
        ),
    ],
)
def test_karaoke_caption_loader_rejects_invalid_token_timing(
    tokens: list[dict[str, object]], diagnostic: str
) -> None:
    manifest_json = {
        "timing_source": "approximate",
        "segments": [
            {
                "segment_id": "segment-001",
                "tokens": tokens,
            }
        ],
    }

    with pytest.raises(KaraokeCaptionError) as error:
        KaraokeCaptionLoader().load_json_dict(manifest_json)

    assert diagnostic in str(error.value)


@pytest.mark.parametrize(
    ("tokens", "diagnostic"),
    [
        ([], "must contain tokens"),
        (
            [
                {"order": 2, "text": "second", "start_seconds": 0.0, "end_seconds": 0.4},
                {"order": 1, "text": "first", "start_seconds": 0.4, "end_seconds": 0.8},
            ],
            "token order must match timing order",
        ),
    ],
)
def test_karaoke_caption_loader_rejects_ambiguous_token_sequences(
    tokens: list[dict[str, object]], diagnostic: str
) -> None:
    manifest_json = {
        "timing_source": "approximate",
        "segments": [
            {
                "segment_id": "segment-001",
                "tokens": tokens,
            }
        ],
    }

    with pytest.raises(KaraokeCaptionError) as error:
        KaraokeCaptionLoader().load_json_dict(manifest_json)

    assert diagnostic in str(error.value)


def test_approximate_karaoke_caption_provider_generates_deterministic_token_timing() -> None:
    provider = ApproximateKaraokeCaptionProvider()

    first = provider.generate_segment(
        segment_id="segment-001",
        narration_text="OpenAI dang build ChatGPT, dung khong?",
        duration_seconds=3.0,
    )
    second = provider.generate_segment(
        segment_id="segment-001",
        narration_text="OpenAI dang build ChatGPT, dung khong?",
        duration_seconds=3.0,
    )

    assert first == second
    assert first.segment_id == "segment-001"
    assert [token.text for token in first.tokens] == [
        "OpenAI",
        "dang",
        "build",
        "ChatGPT",
        "dung",
        "khong",
    ]
    assert [token.order for token in first.tokens] == [1, 2, 3, 4, 5, 6]
    assert first.tokens[0].start_seconds == 0.0
    assert first.tokens[-1].end_seconds == 3.0
    assert all(
        left.end_seconds <= right.start_seconds
        for left, right in zip(first.tokens, first.tokens[1:])
    )


def test_approximate_karaoke_caption_provider_builds_valid_manifest() -> None:
    manifest = ApproximateKaraokeCaptionProvider().generate_manifest(
        (
            ("segment-001", "Xin chao OpenAI.", 1.2),
            ("segment-002", "ChatGPT va Codex.", 1.5),
        )
    )

    loaded = KaraokeCaptionLoader().load(manifest.to_json())

    assert loaded.timing_source == "approximate"
    assert [segment.segment_id for segment in loaded.segments] == [
        "segment-001",
        "segment-002",
    ]
    assert [token.text for token in loaded.segments[1].tokens] == [
        "ChatGPT",
        "va",
        "Codex",
    ]
    assert loaded.segments[0].tokens[-1].end_seconds == 1.2
    assert loaded.segments[1].tokens[-1].end_seconds == 1.5


def test_caption_timing_provider_interface_accepts_precise_provider_double() -> None:
    class PreciseProviderDouble:
        timing_source = "whisper-test-double"

        def generate_manifest(
            self, segments: tuple[tuple[str, str, float], ...]
        ) -> KaraokeCaptionManifest:
            return KaraokeCaptionManifest(
                timing_source=self.timing_source,
                segments=(
                    KaraokeCaptionSegment(
                        segment_id=segments[0][0],
                        tokens=(
                            KaraokeCaptionToken(
                                order=1,
                                text="exact",
                                start_seconds=0.11,
                                end_seconds=0.44,
                            ),
                        ),
                    ),
                ),
            )

    provider: CaptionTimingProvider = PreciseProviderDouble()

    manifest = provider.generate_manifest((("segment-001", "exact", 1.0),))

    assert manifest.timing_source == "whisper-test-double"
    assert manifest.segments[0].tokens[0].start_seconds == 0.11
