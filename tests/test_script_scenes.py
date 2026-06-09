import pytest

from hyperframevideo.script_scenes import (
    ScriptStoryboardError,
    ScriptStoryboardExtractor,
    ScriptScene,
)


def test_extractor_parses_single_segment_with_narration_and_on_screen_text() -> None:
    script_markdown = """Status: approved

## Segment 1

Narration: This is the narration text.

On-screen text: Screen text here.
"""

    scenes = ScriptStoryboardExtractor().extract(script_markdown)

    assert len(scenes) == 1
    scene = scenes[0]
    assert scene.segment_id == "segment-001"
    assert scene.order == 1
    assert scene.narration_text == "This is the narration text."
    assert scene.on_screen_text == "Screen text here."
    assert scene.purpose is None
    assert scene.facts_used is None


def test_extractor_parses_multiple_segments_in_order() -> None:
    script_markdown = """Status: approved

## Segment 1

Narration: First narration.

On-screen text: First screen.

## Segment 2

Narration: Second narration.

On-screen text: Second screen.
"""

    scenes = ScriptStoryboardExtractor().extract(script_markdown)

    assert len(scenes) == 2
    assert scenes[0].segment_id == "segment-001"
    assert scenes[0].order == 1
    assert scenes[0].narration_text == "First narration."
    assert scenes[0].on_screen_text == "First screen."

    assert scenes[1].segment_id == "segment-002"
    assert scenes[1].order == 2
    assert scenes[1].narration_text == "Second narration."
    assert scenes[1].on_screen_text == "Second screen."


def test_extractor_parses_multiline_narration() -> None:
    script_markdown = """Status: approved

## Segment 1

Narration: Line one.
Line two.
Line three.

On-screen text: Screen text.
"""

    scenes = ScriptStoryboardExtractor().extract(script_markdown)

    assert len(scenes) == 1
    scene = scenes[0]
    assert scene.narration_text == "Line one.\nLine two.\nLine three."
    assert scene.on_screen_text == "Screen text."


def test_extractor_parses_optional_purpose_and_facts_used() -> None:
    script_markdown = """Status: approved

## Segment 1

Narration: The narration goes here.

On-screen text: On screen.

Purpose: Explain the context.

Facts used:

* First fact about the topic.
* Second fact with more details.
* Third fact wrapping up.

## Segment 2

Narration: Another segment.

On-screen text: More text on screen.
"""

    scenes = ScriptStoryboardExtractor().extract(script_markdown)

    assert len(scenes) == 2
    scene1 = scenes[0]
    assert scene1.narration_text == "The narration goes here."
    assert scene1.on_screen_text == "On screen."
    assert scene1.purpose == "Explain the context."
    assert scene1.facts_used == (
        "* First fact about the topic.\n"
        "* Second fact with more details.\n"
        "* Third fact wrapping up."
    )

    scene2 = scenes[1]
    assert scene2.narration_text == "Another segment."
    assert scene2.on_screen_text == "More text on screen."
    assert scene2.purpose is None
    assert scene2.facts_used is None


@pytest.mark.parametrize(
    ("script_markdown", "diagnostic"),
    [
        (
            """Status: approved

## Segment 1

On-screen text: Has screen text but no narration.
""",
            "Segment 1 is missing Narration.",
        ),
        (
            """Status: approved

## Segment 1

Narration: Has narration but no on-screen text.
""",
            "Segment 1 is missing On-screen text.",
        ),
        (
            """Status: approved

## Segment 1

Narration: First narration.

On-screen text: First screen.

## Segment 2

On-screen text: Missing narration here.
""",
            "Segment 2 is missing Narration.",
        ),
        (
            """Status: approved

## Segment 1

Narration: First narration.

On-screen text: First screen.

## Segment 2

Narration: Missing on-screen text here.
""",
            "Segment 2 is missing On-screen text.",
        ),
    ],
)
def test_extractor_reports_missing_required_fields(
    script_markdown: str, diagnostic: str
) -> None:
    with pytest.raises(ScriptStoryboardError) as error:
        ScriptStoryboardExtractor().extract(script_markdown)

    assert str(error.value) == diagnostic


def test_extractor_reports_no_segments_found() -> None:
    script_markdown = """Status: approved

This script has no segment blocks.
"""

    with pytest.raises(ScriptStoryboardError) as error:
        ScriptStoryboardExtractor().extract(script_markdown)

    assert str(error.value) == "No segments found in script."
