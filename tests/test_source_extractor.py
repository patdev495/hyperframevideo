from hyperframevideo.models import DirectSourceRequest
import pytest

from hyperframevideo.source_extractor import SourceFetchError, SourceExtractor


class StaticFetcher:
    def __init__(self, html: str) -> None:
        self.html = html
        self.urls: list[str] = []

    def fetch(self, url: str) -> str:
        self.urls.append(url)
        return self.html


class StaticBrowserRenderer:
    def __init__(self, html: str) -> None:
        self.html = html
        self.urls: list[str] = []

    def render(self, url: str) -> str:
        self.urls.append(url)
        return self.html


class FailingFetcher:
    def fetch(self, url: str) -> str:
        raise SourceFetchError(f"Failed to fetch source URL: {url}")


def test_source_extractor_returns_typed_content_from_readable_html() -> None:
    html = """
    <html>
      <head>
        <meta property="og:site_name" content="Example News">
        <meta property="article:published_time" content="2026-06-08T08:00:00Z">
        <title>Fallback title</title>
      </head>
      <body>
        <article>
          <h1>AI chips are getting faster</h1>
          <p>A new accelerator was announced for local AI workloads.</p>
          <p>The company says the chip improves inference speed for small teams.</p>
        </article>
      </body>
    </html>
    """
    fetcher = StaticFetcher(html)
    extractor = SourceExtractor(fetcher=fetcher)

    extracted = extractor.extract(
        DirectSourceRequest(source_url="https://example.com/ai-chip")
    )

    assert extracted.source_url == "https://example.com/ai-chip"
    assert extracted.title == "AI chips are getting faster"
    assert "local AI workloads" in extracted.text
    assert extracted.source_name == "Example News"
    assert extracted.published_at == "2026-06-08T08:00:00Z"
    assert extracted.extraction_method == "readability"
    assert fetcher.urls == ["https://example.com/ai-chip"]


def test_source_extractor_falls_back_to_browser_rendering_for_low_content() -> None:
    fetcher = StaticFetcher("<html><body><div id='app'></div></body></html>")
    browser_renderer = StaticBrowserRenderer(
        """
        <html>
          <head><title>Rendered title</title></head>
          <body>
            <article>
              <h1>Rendered AI story</h1>
              <p>JavaScript rendered the article body after the initial fetch.</p>
              <p>The rendered page now has enough source content to use.</p>
            </article>
          </body>
        </html>
        """
    )
    extractor = SourceExtractor(fetcher=fetcher, browser_renderer=browser_renderer)

    extracted = extractor.extract(
        DirectSourceRequest(source_url="https://example.com/rendered-ai-story")
    )

    assert extracted.title == "Rendered AI story"
    assert "enough source content" in extracted.text
    assert extracted.extraction_method == "playwright"
    assert fetcher.urls == ["https://example.com/rendered-ai-story"]
    assert browser_renderer.urls == ["https://example.com/rendered-ai-story"]


def test_source_extractor_returns_actionable_fetch_error() -> None:
    extractor = SourceExtractor(fetcher=FailingFetcher())

    with pytest.raises(SourceFetchError, match="https://example.com/missing"):
        extractor.extract(DirectSourceRequest(source_url="https://example.com/missing"))
