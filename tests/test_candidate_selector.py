from io import StringIO

from hyperframevideo.candidate_selector import CandidateSelector
from hyperframevideo.models import NewsCandidate


def test_candidate_selector_prints_menu_and_returns_selected_candidate() -> None:
    candidates = [
        NewsCandidate(
            url="https://example.com/one",
            title="Story One",
            source_name="Example News",
            published_at="2026-06-09",
            summary="First candidate.",
        ),
        NewsCandidate(
            url="https://example.com/two",
            title="Story Two",
            source_name=None,
            published_at=None,
            summary=None,
        ),
    ]
    output = StringIO()
    selector = CandidateSelector(input_stream=StringIO("2\n"), output_stream=output)

    selected = selector.select(candidates)

    assert selected == candidates[1]
    menu = output.getvalue()
    assert "1. Story One" in menu
    assert "Example News" in menu
    assert "2026-06-09" in menu
    assert "First candidate." in menu
    assert "2. Story Two" in menu
    assert "unknown" in menu
    assert "no summary" in menu


def test_candidate_selector_reprompts_after_invalid_input() -> None:
    candidates = [
        NewsCandidate(
            url="https://example.com/one",
            title="Story One",
            source_name="Example News",
            published_at="2026-06-09",
            summary="First candidate.",
        )
    ]
    output = StringIO()
    selector = CandidateSelector(input_stream=StringIO("bad\n3\n1\n"), output_stream=output)

    selected = selector.select(candidates)

    assert selected == candidates[0]
    assert output.getvalue().count("Enter a candidate number") == 3
    assert "Invalid selection." in output.getvalue()


def test_candidate_selector_returns_none_for_rerun_signal() -> None:
    candidates = [
        NewsCandidate(
            url="https://example.com/one",
            title="Story One",
            source_name="Example News",
            published_at="2026-06-09",
            summary="First candidate.",
        )
    ]

    assert (
        CandidateSelector(input_stream=StringIO("0\n"), output_stream=StringIO()).select(
            candidates
        )
        is None
    )
    assert (
        CandidateSelector(input_stream=StringIO("q\n"), output_stream=StringIO()).select(
            candidates
        )
        is None
    )
