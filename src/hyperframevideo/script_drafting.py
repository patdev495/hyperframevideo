from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from hyperframevideo.source_evidence import SourceEvidence


@dataclass(frozen=True, slots=True)
class ScriptDraftingPrompt:
    text: str


@dataclass(frozen=True, slots=True)
class ScriptDraftingResult:
    script_markdown: str
    provider_name: str
    model: str
    warnings: tuple[str, ...] = ()
    raw_usage: dict[str, Any] | None = None


class ScriptDraftingProvider(Protocol):
    provider_name: str

    def draft_script(
        self, source_evidence: SourceEvidence, prompt: ScriptDraftingPrompt
    ) -> ScriptDraftingResult:
        """Draft a Source-Grounded Script artifact from Source Evidence."""

    def repair_script(
        self,
        malformed_script_markdown: str,
        source_evidence: SourceEvidence,
        prompt: ScriptDraftingPrompt,
        *,
        max_attempts: int = 1,
    ) -> ScriptDraftingResult:
        """Repair malformed Source-Grounded Script output with bounded attempts."""
