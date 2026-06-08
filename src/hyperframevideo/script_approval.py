from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ScriptApprovalResult:
    is_approved: bool
    status: str | None
    diagnostic: str | None


@dataclass(frozen=True, slots=True)
class ScriptApprovalGate:
    def evaluate(self, script_markdown: str) -> ScriptApprovalResult:
        status = self._parse_status(script_markdown)

        if status == "approved":
            return ScriptApprovalResult(
                is_approved=True,
                status=status,
                diagnostic=None,
            )
        if status == "draft":
            return ScriptApprovalResult(
                is_approved=False,
                status=status,
                diagnostic="Script is still draft.",
            )

        return ScriptApprovalResult(
            is_approved=False,
            status=status,
            diagnostic=(
                "Script status is missing."
                if status is None
                else f"Unsupported script status: {status}."
            ),
        )

    def _parse_status(self, script_markdown: str) -> str | None:
        for line in script_markdown.splitlines():
            normalized_line = line.strip()
            label, separator, value = normalized_line.partition(":")
            if separator and label.strip().lower() == "status":
                return value.strip().lower()
        return None
