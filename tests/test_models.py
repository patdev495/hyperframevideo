from hyperframevideo.models import DirectSourceRequest


def test_direct_source_request_preserves_source_url() -> None:
    request = DirectSourceRequest(source_url="https://example.com/news/story")

    assert request.source_url == "https://example.com/news/story"
