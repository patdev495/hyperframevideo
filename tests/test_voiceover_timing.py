import pytest

from hyperframevideo.voiceover_timing import (
    VoiceoverTimingError,
    VoiceoverTimingLoader,
)


def test_voiceover_timing_loader_returns_ordered_timing_entries() -> None:
    manifest_json = """
{
  "provider_name": "vieneu",
  "segments": [
    {
      "segment_id": "segment-002",
      "order": 2,
      "narration_text": "Second narration.",
      "audio_path": "voiceover/segment-002.wav",
      "duration_seconds": 2.5,
      "warnings": ["trimmed silence"]
    },
    {
      "segment_id": "segment-001",
      "order": 1,
      "narration_text": "First narration.",
      "audio_path": "voiceover/segment-001.wav",
      "duration_seconds": 1.25,
      "warnings": []
    }
  ]
}
"""

    timing = VoiceoverTimingLoader().load(manifest_json)

    assert [entry.segment_id for entry in timing] == [
        "segment-001",
        "segment-002",
    ]
    assert [entry.order for entry in timing] == [1, 2]
    assert [entry.narration_text for entry in timing] == [
        "First narration.",
        "Second narration.",
    ]
    assert [entry.audio_path for entry in timing] == [
        "voiceover/segment-001.wav",
        "voiceover/segment-002.wav",
    ]
    assert [entry.duration_seconds for entry in timing] == [1.25, 2.5]
    assert timing[1].warnings == ("trimmed silence",)


@pytest.mark.parametrize(
    ("manifest_json", "diagnostic"),
    [
        (
            '{"segments": []}',
            "voiceover.json is missing provider_name.",
        ),
        (
            '{"provider_name": "vieneu"}',
            "voiceover.json is missing segments.",
        ),
        (
            '{"provider_name": "vieneu", "segments": [null]}',
            "Voiceover segment 1 must be an object.",
        ),
        (
            """
            {
              "provider_name": "vieneu",
              "segments": [
                {
                  "segment_id": "segment-001",
                  "order": 1,
                  "narration_text": "Narration.",
                  "audio_path": "voiceover/segment-001.wav",
                  "duration_seconds": 0,
                  "warnings": []
                }
              ]
            }
            """,
            "Voiceover segment 1 duration_seconds must be positive.",
        ),
    ],
)
def test_voiceover_timing_loader_reports_malformed_manifest_readably(
    manifest_json: str, diagnostic: str
) -> None:
    with pytest.raises(VoiceoverTimingError) as error:
        VoiceoverTimingLoader().load(manifest_json)

    assert str(error.value) == diagnostic
