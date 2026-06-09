import pytest

from hyperframevideo.voiceover_segments import (
    VoiceoverNarrationError,
    VoiceoverNarrationExtractor,
)


def test_voiceover_narration_extractor_returns_ordered_segments() -> None:
    script = """
Status: approved
Language: en

# Source-Grounded Script

## Segment 1
Narration: First spoken line.
On-screen text: First caption.

## Segment 2
Narration: Second spoken line.
On-screen text: Second caption.
"""

    segments = VoiceoverNarrationExtractor().extract(script)

    assert [segment.segment_id for segment in segments] == [
        "segment-001",
        "segment-002",
    ]
    assert [segment.order for segment in segments] == [1, 2]
    assert [segment.narration_text for segment in segments] == [
        "First spoken line.",
        "Second spoken line.",
    ]


def test_voiceover_narration_extractor_rejects_script_without_narration() -> None:
    script = """
Status: approved
Language: en

# Source-Grounded Script

## Segment 1
On-screen text: Caption without spoken text.
"""

    with pytest.raises(VoiceoverNarrationError) as error:
        VoiceoverNarrationExtractor().extract(script)

    assert str(error.value) == "Approved script contains no Narration lines."


def test_voiceover_narration_extractor_rejects_blank_narration() -> None:
    script = """
Status: approved
Language: en

# Source-Grounded Script

## Segment 1
Narration:

## Segment 2
Narration: Spoken line.
"""

    with pytest.raises(VoiceoverNarrationError) as error:
        VoiceoverNarrationExtractor().extract(script)

    assert str(error.value) == "Narration line 1 is blank."
