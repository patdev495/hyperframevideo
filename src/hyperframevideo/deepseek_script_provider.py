from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Callable

from hyperframevideo.script_drafting import (
    ScriptDraftingPrompt,
    ScriptDraftingResult,
)
from hyperframevideo.source_evidence import SourceEvidence


class ScriptDraftingProviderError(Exception):
    pass


PostJson = Callable[[str, dict[str, Any], dict[str, str], float], dict[str, Any]]


def _urllib_post_json(
    url: str, payload: dict[str, Any], headers: dict[str, str], timeout: float
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        diagnostic = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {error.code}: {diagnostic}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(str(error.reason)) from error
    return json.loads(response_body)


@dataclass(frozen=True, slots=True)
class DeepSeekScriptDraftingProvider:
    api_key: str
    base_url: str = "https://api.deepseek.com"
    model: str = "deepseek-chat"
    timeout_seconds: float = 60.0
    post_json: PostJson = field(default=_urllib_post_json, repr=False, compare=False)
    provider_name: str = "deepseek"

    @classmethod
    def from_environment(
        cls, *, model_override: str | None = None
    ) -> "DeepSeekScriptDraftingProvider":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ScriptDraftingProviderError(
                "DEEPSEEK_API_KEY is required for --script-provider deepseek."
            )
        return cls(
            api_key=api_key,
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=model_override
            or os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        )

    def draft_script(
        self, source_evidence: SourceEvidence, prompt: ScriptDraftingPrompt
    ) -> ScriptDraftingResult:
        return self._complete(
            self._draft_messages(source_evidence, prompt),
            warning_prefix=(),
        )

    def repair_script(
        self,
        malformed_script_markdown: str,
        source_evidence: SourceEvidence,
        prompt: ScriptDraftingPrompt,
        *,
        max_attempts: int = 1,
    ) -> ScriptDraftingResult:
        if max_attempts < 1:
            raise ScriptDraftingProviderError("Script repair requires at least one attempt.")
        repair_prompt = (
            f"{prompt.text}\n\n"
            "Repair this malformed SCRIPT.md. Return SCRIPT.md only and keep it "
            "source-grounded.\n\n"
            f"Malformed SCRIPT.md:\n{malformed_script_markdown}"
        )
        return self._complete(
            self._draft_messages(source_evidence, ScriptDraftingPrompt(repair_prompt)),
            warning_prefix=("repaired-script-output",),
        )

    def _draft_messages(
        self, source_evidence: SourceEvidence, prompt: ScriptDraftingPrompt
    ) -> list[dict[str, str]]:
        evidence_json = json.dumps(source_evidence.to_json_dict(), ensure_ascii=False)
        return [
            {
                "role": "user",
                "content": f"{prompt.text}\n\nSource Evidence JSON:\n{evidence_json}",
            }
        ]

    def _complete(
        self,
        messages: list[dict[str, str]],
        *,
        warning_prefix: tuple[str, ...],
    ) -> ScriptDraftingResult:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        try:
            response = self.post_json(url, payload, headers, self.timeout_seconds)
        except Exception as error:
            raise ScriptDraftingProviderError(
                f"DeepSeek request failed: {error}"
            ) from error

        try:
            script_markdown = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise ScriptDraftingProviderError(
                "DeepSeek response did not include message content."
            ) from error

        return ScriptDraftingResult(
            script_markdown=script_markdown,
            provider_name=self.provider_name,
            model=self.model,
            warnings=warning_prefix,
            raw_usage=response.get("usage"),
        )
