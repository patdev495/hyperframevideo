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


def test_voiceover_narration_extractor_accepts_multiline_narration_blocks() -> None:
    script = """
Status: approved
Language: vi

# Source-Grounded Script

## Segment 1
Narration:
Dong mo dau.
Dong tiep theo.

On-screen text:
Caption.

## Segment 2
Narration:
Doan thu hai.

Purpose:
Explain the next point.
"""

    segments = VoiceoverNarrationExtractor().extract(script)

    assert [segment.segment_id for segment in segments] == [
        "segment-001",
        "segment-002",
    ]
    assert segments[0].narration_text == "Dong mo dau.\nDong tiep theo."
    assert segments[1].narration_text == "Doan thu hai."


def test_voiceover_narration_extractor_accepts_markdown_bold_field_labels() -> None:
    script = """
**Status:** approved
**Language:** en

# Source-Grounded Script

## Segment 1
**Narration:** First spoken line.
**On-screen text:** First caption.

## Segment 2
**Narration:** Second spoken line.
**On-screen text:** Second caption.
"""

    segments = VoiceoverNarrationExtractor().extract(script)

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
