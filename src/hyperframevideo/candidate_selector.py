from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import TextIO, Sequence

from hyperframevideo.models import NewsCandidate


@dataclass(frozen=True, slots=True)
class CandidateSelector:
    input_stream: TextIO = field(default_factory=lambda: sys.stdin)
    output_stream: TextIO = field(default_factory=lambda: sys.stdout)

    def select(self, candidates: Sequence[NewsCandidate]) -> NewsCandidate | None:
        self._print_menu(candidates)
        while True:
            self._print_prompt()
            raw_choice = self.input_stream.readline()
            if raw_choice == "":
                return None

            choice = raw_choice.strip()
            if choice.lower() == "q":
                return None

            try:
                index = int(choice)
            except ValueError:
                print("Invalid selection.", file=self.output_stream)
                continue

            if index == 0:
                return None

            if 1 <= index <= len(candidates):
                return candidates[index - 1]

            print("Invalid selection.", file=self.output_stream)

    def _print_menu(self, candidates: Sequence[NewsCandidate]) -> None:
        for index, candidate in enumerate(candidates, start=1):
            source_name = candidate.source_name or "unknown"
            published_at = candidate.published_at or "unknown"
            summary = candidate.summary or "no summary"
            print(
                f"{index}. {candidate.title} | {source_name} | {published_at} | {summary}",
                file=self.output_stream,
            )

    def _print_prompt(self) -> None:
        print(
            "Enter a candidate number, 0 to search again, or q to quit:",
            file=self.output_stream,
        )
