import json
from pathlib import Path

import pytest

from hyperframevideo.deepseek_script_provider import (
    DeepSeekScriptDraftingProvider,
    ScriptDraftingProviderError,
)
from hyperframevideo.script_drafting import (
    ScriptDraftingPrompt,
    ScriptDraftingProvider,
    ScriptDraftingResult,
)
from hyperframevideo.source_evidence import SourceEvidence


class FakeScriptDraftingProvider(ScriptDraftingProvider):
    provider_name = "fake-script-provider"

    def draft_script(
        self, source_evidence: SourceEvidence, prompt: ScriptDraftingPrompt
    ) -> ScriptDraftingResult:
        assert "SCRIPT.md only" in prompt.text
        return ScriptDraftingResult(
            script_markdown=(
                "Status: draft\n"
                "Language: en\n\n"
                "# Source-Grounded Script\n\n"
                "## Segment 1\n"
                "Narration: Draft from fixture evidence.\n"
            ),
            provider_name=self.provider_name,
            model="fake-model",
            warnings=("fixture-warning",),
            raw_usage={"total_tokens": 12},
        )

    def repair_script(
        self,
        malformed_script_markdown: str,
        source_evidence: SourceEvidence,
        prompt: ScriptDraftingPrompt,
        *,
        max_attempts: int = 1,
    ) -> ScriptDraftingResult:
        assert max_attempts == 1
        assert malformed_script_markdown == "bad"
        return ScriptDraftingResult(
            script_markdown="Status: draft\nLanguage: en\n\n# Source-Grounded Script\n",
            provider_name=self.provider_name,
            model="fake-model",
            warnings=("repaired",),
            raw_usage=None,
        )


def _source_evidence() -> SourceEvidence:
    return SourceEvidence(
        url="https://example.com/story",
        title="Fixture story",
        source_name="Example",
        published_at="2026-06-09",
        extracted_text="Fixture source evidence text.",
        extraction_method="readability",
        warnings=(),
    )


def test_fake_script_drafting_provider_drafts_source_grounded_script() -> None:
    provider = FakeScriptDraftingProvider()
    result = provider.draft_script(
        _source_evidence(), ScriptDraftingPrompt("Produce SCRIPT.md only")
    )

    assert result.provider_name == "fake-script-provider"
    assert result.model == "fake-model"
    assert result.script_markdown.startswith("Status: draft")
    assert result.warnings == ("fixture-warning",)
    assert result.raw_usage == {"total_tokens": 12}


def test_fake_script_drafting_provider_repairs_malformed_script_once() -> None:
    provider = FakeScriptDraftingProvider()

    result = provider.repair_script(
        "bad",
        _source_evidence(),
        ScriptDraftingPrompt("Produce SCRIPT.md only"),
        max_attempts=1,
    )

    assert "Status: draft" in result.script_markdown
    assert result.warnings == ("repaired",)


def test_deepseek_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(ScriptDraftingProviderError, match="DEEPSEEK_API_KEY"):
        DeepSeekScriptDraftingProvider.from_environment()


def test_deepseek_provider_reads_environment_and_model_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://deepseek.local")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-env")

    provider = DeepSeekScriptDraftingProvider.from_environment(model_override="deepseek-cli")

    assert provider.base_url == "https://deepseek.local"
    assert provider.model == "deepseek-cli"


def test_deepseek_provider_returns_script_and_metadata() -> None:
    calls = []

    def fake_post(url, payload, headers, timeout):
        calls.append((url, payload, headers, timeout))
        return {
            "choices": [{"message": {"content": "Status: draft\nLanguage: en\n"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }

    provider = DeepSeekScriptDraftingProvider(
        api_key="secret",
        base_url="https://deepseek.local",
        model="deepseek-chat",
        post_json=fake_post,
    )

    result = provider.draft_script(
        _source_evidence(), ScriptDraftingPrompt("Draft from evidence")
    )

    assert calls[0][0] == "https://deepseek.local/chat/completions"
    assert calls[0][1]["model"] == "deepseek-chat"
    assert "Draft from evidence" in calls[0][1]["messages"][0]["content"]
    assert json.dumps(_source_evidence().to_json_dict()) in calls[0][1]["messages"][0]["content"]
    assert calls[0][2]["Authorization"] == "Bearer secret"
    assert result.script_markdown == "Status: draft\nLanguage: en\n"
    assert result.provider_name == "deepseek"
    assert result.model == "deepseek-chat"
    assert result.raw_usage == {"prompt_tokens": 10, "completion_tokens": 20}


def test_deepseek_provider_errors_are_readable() -> None:
    def fake_post(url, payload, headers, timeout):
        raise RuntimeError("HTTP 500 upstream")

    provider = DeepSeekScriptDraftingProvider(
        api_key="secret",
        model="deepseek-chat",
        post_json=fake_post,
    )

    with pytest.raises(ScriptDraftingProviderError, match="DeepSeek request failed"):
        provider.draft_script(_source_evidence(), ScriptDraftingPrompt("Draft"))
