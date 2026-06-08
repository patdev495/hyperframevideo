from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from readability import Document

from hyperframevideo.models import DirectSourceRequest, ExtractedSource


class SourceFetchError(Exception):
    pass


class SourceFetcher(Protocol):
    def fetch(self, url: str) -> str:
        pass


class BrowserRenderer(Protocol):
    def render(self, url: str) -> str:
        pass


class UrlLibSourceFetcher:
    def fetch(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": "hyperframevideo/0.1"})
        try:
            with urlopen(request, timeout=20) as response:
                return response.read().decode("utf-8", errors="replace")
        except OSError as error:
            raise SourceFetchError(f"Failed to fetch source URL: {url}") from error


class PlaywrightBrowserRenderer:
    def render(self, url: str) -> str:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise SourceFetchError(
                "Playwright fallback requires the 'playwright' package to be installed."
            ) from error

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(url, wait_until="networkidle", timeout=20_000)
                return page.content()
            finally:
                browser.close()


@dataclass(frozen=True, slots=True)
class SourceExtractor:
    fetcher: SourceFetcher = field(default_factory=UrlLibSourceFetcher)
    browser_renderer: BrowserRenderer = field(default_factory=PlaywrightBrowserRenderer)
    minimum_text_length: int = 80

    def extract(self, request: DirectSourceRequest) -> ExtractedSource:
        html = self.fetcher.fetch(request.source_url)
        extracted = self._extract_readable_html(
            request.source_url, html, extraction_method="readability"
        )
        if len(extracted.text) >= self.minimum_text_length:
            return extracted

        rendered_html = self.browser_renderer.render(request.source_url)
        return self._extract_readable_html(
            request.source_url, rendered_html, extraction_method="playwright"
        )

    def _extract_readable_html(
        self, source_url: str, html: str, extraction_method: str
    ) -> ExtractedSource:
        source_soup = BeautifulSoup(html, "html.parser")
        document = Document(html)
        readable_soup = BeautifulSoup(document.summary(), "html.parser")
        readable = readable_soup.find("article") or readable_soup.body or readable_soup

        title = self._first_text(
            readable.find("h1") if readable else None,
            source_soup.find("h1"),
            source_soup.find("title"),
        )
        if not title:
            title = document.short_title()
        text = "\n\n".join(
            paragraph.get_text(" ", strip=True)
            for paragraph in readable.find_all("p")
            if paragraph.get_text(" ", strip=True)
        )

        return ExtractedSource(
            source_url=source_url,
            title=title,
            text=text,
            source_name=self._meta_content(source_soup, "property", "og:site_name"),
            published_at=self._meta_content(
                source_soup, "property", "article:published_time"
            ),
            extraction_method=extraction_method,
        )

    def _first_text(self, *nodes: object) -> str:
        for node in nodes:
            if node is None:
                continue
            text = node.get_text(" ", strip=True)
            if text:
                return text
        return ""

    def _meta_content(self, soup: BeautifulSoup, attr: str, value: str) -> str | None:
        node = soup.find("meta", attrs={attr: value})
        if node is None:
            return None
        content = node.get("content")
        return str(content) if content else None
