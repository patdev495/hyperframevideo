from __future__ import annotations

from dataclasses import dataclass

from hyperframevideo.source_evidence import SourceEvidence


@dataclass(frozen=True, slots=True)
class StoryArtifacts:
    selected_story_markdown: str
    script_markdown: str


@dataclass(frozen=True, slots=True)
class StoryArtifactGenerator:
    language: str = "en"
    target_duration: str = "60-90 seconds"
    visual_treatment: str = "tech-hype"

    def generate(self, evidence: SourceEvidence) -> StoryArtifacts:
        return StoryArtifacts(
            selected_story_markdown=self._selected_story(evidence),
            script_markdown=self._script(evidence),
        )

    def _selected_story(self, evidence: SourceEvidence) -> str:
        source_name = evidence.source_name or "Unknown source"
        published_at = evidence.published_at or "Unknown publish date"
        warnings = "\n".join(f"- {warning}" for warning in evidence.warnings) or "- None"

        return (
            "# Selected Story\n\n"
            f"Title: {evidence.title}\n"
            f"Source: {source_name}\n"
            f"URL: {evidence.url}\n"
            f"Published: {published_at}\n"
            f"Extraction Method: {evidence.extraction_method}\n\n"
            "## Story Context\n\n"
            f"{self._excerpt(evidence.extracted_text)}\n\n"
            "## Source Warnings\n\n"
            f"{warnings}\n"
        )

    def _script(self, evidence: SourceEvidence) -> str:
        title = evidence.title or "Untitled Source Story"
        fact = self._excerpt(evidence.extracted_text)
        warnings = "\n".join(f"- {warning}" for warning in evidence.warnings) or "- None"

        return (
            "Status: draft\n"
            f"Language: {self.language}\n"
            f"Target Duration: {self.target_duration}\n"
            f"Visual Treatment: {self.visual_treatment}\n\n"
            "# Title\n\n"
            f"{title}\n\n"
            "# Hook\n\n"
            "Draft a curiosity-driven opening that stays grounded in the source evidence.\n\n"
            "# Source-Grounded Script\n\n"
            "## Segment 1\n"
            "Narration: Draft narration from the source evidence without copying long passages.\n"
            "On-screen text: Short text that highlights the core development.\n"
            "Purpose: Establish why this story matters to the viewer.\n"
            "Facts used:\n"
            f"- {fact}\n\n"
            "# Fact Check\n\n"
            f"- Claim: Core facts must be checked against the selected source.\n"
            f"  Source: {evidence.url}\n\n"
            "# Production Notes\n\n"
            f"- Source warnings: {warnings}\n"
            "- Keep the script within the target duration before Script Approval.\n"
        )

    def _excerpt(self, text: str) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= 240:
            return normalized
        return f"{normalized[:237]}..."
