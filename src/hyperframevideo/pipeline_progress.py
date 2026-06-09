from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class PipelineProgressEvent:
    phase: str
    status: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    message: str = ""
    artifact_path: Path | None = None
    provider_name: str | None = None
    model: str | None = None
    error: str | None = None

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "artifact_path": (
                self.artifact_path.as_posix() if self.artifact_path is not None else None
            ),
            "provider_name": self.provider_name,
            "model": self.model,
            "error": self.error,
        }

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "PipelineProgressEvent":
        artifact = payload.get("artifact_path")
        return cls(
            phase=payload["phase"],
            status=payload["status"],
            timestamp=datetime.fromisoformat(payload["timestamp"]),
            message=payload.get("message") or "",
            artifact_path=Path(artifact) if artifact else None,
            provider_name=payload.get("provider_name"),
            model=payload.get("model"),
            error=payload.get("error"),
        )


@dataclass(frozen=True, slots=True)
class PipelineProgressLog:
    path: Path

    def append(self, event: PipelineProgressEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(format_progress_jsonl(event))
            handle.write("\n")

    def read(self) -> list[PipelineProgressEvent]:
        if not self.path.exists():
            return []
        return [
            PipelineProgressEvent.from_json_dict(json.loads(line))
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]


def format_progress_text(event: PipelineProgressEvent) -> str:
    message = f" - {event.message}" if event.message else ""
    artifact = f" ({event.artifact_path.as_posix()})" if event.artifact_path else ""
    provider = ""
    if event.provider_name:
        provider = f" [{event.provider_name}"
        if event.model:
            provider += f":{event.model}"
        provider += "]"
    error = f" Error: {event.error}" if event.error else ""
    return f"[{event.phase}] {event.status}{provider}{message}{artifact}{error}"


def format_progress_jsonl(event: PipelineProgressEvent) -> str:
    return json.dumps(event.to_json_dict(), separators=(",", ":"))
