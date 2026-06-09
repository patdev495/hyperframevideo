from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from typing import Any, Protocol


class KaraokeCaptionError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class KaraokeCaptionToken:
    order: int
    text: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True, slots=True)
class KaraokeCaptionSegment:
    segment_id: str
    tokens: tuple[KaraokeCaptionToken, ...]

    def phrase_windows(
        self, *, max_tokens: int
    ) -> tuple[tuple[KaraokeCaptionToken, ...], ...]:
        if max_tokens <= 0:
            raise KaraokeCaptionError("max_tokens must be positive.")

        return tuple(
            self.tokens[index : index + max_tokens]
            for index in range(0, len(self.tokens), max_tokens)
        )


@dataclass(frozen=True, slots=True)
class KaraokeCaptionManifest:
    timing_source: str
    segments: tuple[KaraokeCaptionSegment, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_json_dict(), indent=2, ensure_ascii=False)


class CaptionTimingProvider(Protocol):
    timing_source: str

    def generate_manifest(
        self, segments: tuple[tuple[str, str, float], ...]
    ) -> KaraokeCaptionManifest:
        pass


@dataclass(frozen=True, slots=True)
class KaraokeCaptionLoader:
    def load(self, manifest_json: str) -> KaraokeCaptionManifest:
        try:
            payload = json.loads(manifest_json)
        except json.JSONDecodeError as error:
            raise KaraokeCaptionError(
                f"Invalid karaoke caption JSON: {error.msg}."
            ) from error

        return self.load_json_dict(payload)

    def load_json_dict(self, payload: dict[str, Any]) -> KaraokeCaptionManifest:
        if not isinstance(payload, dict):
            raise KaraokeCaptionError("Karaoke caption manifest must be a JSON object.")

        timing_source = payload.get("timing_source")
        if not isinstance(timing_source, str) or not timing_source:
            raise KaraokeCaptionError("Karaoke caption manifest is missing timing_source.")

        segments = payload.get("segments")
        if not isinstance(segments, list):
            raise KaraokeCaptionError("Karaoke caption manifest is missing segments.")

        manifest = KaraokeCaptionManifest(
            timing_source=timing_source,
            segments=tuple(
                self._load_segment(segment, index=index)
                for index, segment in enumerate(segments, start=1)
            ),
        )
        self._validate_manifest(manifest)
        return manifest

    def _load_segment(self, segment: Any, index: int) -> KaraokeCaptionSegment:
        if not isinstance(segment, dict):
            raise KaraokeCaptionError(f"Karaoke caption segment {index} must be an object.")

        segment_id = segment.get("segment_id")
        if not isinstance(segment_id, str) or not segment_id:
            raise KaraokeCaptionError(
                f"Karaoke caption segment {index} is missing segment_id."
            )

        tokens = segment.get("tokens")
        if not isinstance(tokens, list):
            raise KaraokeCaptionError(
                f"Karaoke caption segment {index} is missing tokens."
            )

        return KaraokeCaptionSegment(
            segment_id=segment_id,
            tokens=tuple(
                self._load_token(token, segment_index=index, token_index=token_index)
                for token_index, token in enumerate(tokens, start=1)
            ),
        )

    def _load_token(
        self, token: Any, *, segment_index: int, token_index: int
    ) -> KaraokeCaptionToken:
        if not isinstance(token, dict):
            raise KaraokeCaptionError(
                f"Karaoke caption segment {segment_index} token {token_index} must be an object."
            )

        order = token.get("order")
        text = token.get("text")
        start_seconds = token.get("start_seconds")
        end_seconds = token.get("end_seconds")

        if not isinstance(order, int):
            raise KaraokeCaptionError(
                f"Karaoke caption segment {segment_index} token {token_index} is missing order."
            )
        if not isinstance(text, str) or not text:
            raise KaraokeCaptionError(
                f"Karaoke caption segment {segment_index} token {token_index} is missing text."
            )
        if not isinstance(start_seconds, int | float):
            raise KaraokeCaptionError(
                f"Karaoke caption segment {segment_index} token {token_index} is missing start_seconds."
            )
        if not isinstance(end_seconds, int | float):
            raise KaraokeCaptionError(
                f"Karaoke caption segment {segment_index} token {token_index} is missing end_seconds."
            )

        return KaraokeCaptionToken(
            order=order,
            text=text,
            start_seconds=float(start_seconds),
            end_seconds=float(end_seconds),
        )

    def _validate_manifest(self, manifest: KaraokeCaptionManifest) -> None:
        for segment in manifest.segments:
            if not segment.tokens:
                raise KaraokeCaptionError(
                    f"Karaoke caption segment {segment.segment_id} must contain tokens."
                )
            previous_end = 0.0
            for expected_order, token in enumerate(segment.tokens, start=1):
                if token.order != expected_order:
                    raise KaraokeCaptionError(
                        f"Karaoke caption segment {segment.segment_id} "
                        "token order must match timing order."
                    )
                if token.start_seconds < 0:
                    raise KaraokeCaptionError(
                        f"Karaoke caption token {token.order} in {segment.segment_id} "
                        "must be segment-relative."
                    )
                if token.end_seconds <= token.start_seconds:
                    raise KaraokeCaptionError(
                        f"Karaoke caption token {token.order} in {segment.segment_id} "
                        "end_seconds must be greater than start_seconds."
                    )
                if token.start_seconds < previous_end:
                    raise KaraokeCaptionError(
                        f"Karaoke caption token {token.order} in {segment.segment_id} "
                        "must not overlap the previous token."
                    )
                previous_end = token.end_seconds


@dataclass(frozen=True, slots=True)
class ApproximateKaraokeCaptionProvider:
    timing_source: str = "approximate"

    def generate_segment(
        self, *, segment_id: str, narration_text: str, duration_seconds: float
    ) -> KaraokeCaptionSegment:
        if duration_seconds <= 0:
            raise KaraokeCaptionError("duration_seconds must be positive.")

        words = self._tokenize(narration_text)
        if not words:
            raise KaraokeCaptionError("narration_text must contain caption tokens.")

        token_duration = duration_seconds / len(words)
        tokens = []
        for index, word in enumerate(words):
            start = token_duration * index
            end = duration_seconds if index == len(words) - 1 else token_duration * (index + 1)
            tokens.append(
                KaraokeCaptionToken(
                    order=index + 1,
                    text=word,
                    start_seconds=round(start, 3),
                    end_seconds=round(end, 3),
                )
            )

        return KaraokeCaptionSegment(segment_id=segment_id, tokens=tuple(tokens))

    def generate_manifest(
        self, segments: tuple[tuple[str, str, float], ...]
    ) -> KaraokeCaptionManifest:
        return KaraokeCaptionManifest(
            timing_source=self.timing_source,
            segments=tuple(
                self.generate_segment(
                    segment_id=segment_id,
                    narration_text=narration_text,
                    duration_seconds=duration_seconds,
                )
                for segment_id, narration_text, duration_seconds in segments
            ),
        )

    def _tokenize(self, text: str) -> tuple[str, ...]:
        return tuple(re.findall(r"[\w]+", text, flags=re.UNICODE))
