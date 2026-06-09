from __future__ import annotations

import argparse
import datetime
import json
import sys

from hyperframevideo import __version__
from hyperframevideo.candidate_selector import CandidateSelector
from hyperframevideo.discovery_engine import DiscoveryEngine
from hyperframevideo.models import DirectSourceRequest, DiscoveryRequest, NewsCandidate
from hyperframevideo.news_candidate_builder import NewsCandidateBuilder
from hyperframevideo.production_runs import ProductionRunStore
from hyperframevideo.source_evidence import SourceEvidenceBuilder
from hyperframevideo.source_extractor import SourceExtractor
from hyperframevideo.story_artifacts import StoryArtifactGenerator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyperframe-video",
        description="Local-first News-to-Video Pipeline CLI.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the CLI version and exit.",
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="The source URL to process.",
    )
    parser.add_argument(
        "--run-id",
        help="The custom ID for the production run. If not provided, one will be generated.",
    )
    parser.add_argument(
        "--discover",
        help="Discover current news candidates for the given query.",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=5,
        help="The number of discovery candidates to show.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"hyperframevideo {__version__}")
        return 0

    if args.url and args.discover:
        parser.error("Provide either a source URL or --discover, not both.")

    if not args.url and not args.discover:
        parser.print_help()
        return 0

    run_id = args.run_id
    if not run_id:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"run_{timestamp}"

    selected_candidate: NewsCandidate | None = None
    candidates: list[NewsCandidate] = []

    try:
        source_url = args.url
        if args.discover:
            discovery_request = DiscoveryRequest(
                query=args.discover, candidate_count=args.candidates
            )
            engine = DiscoveryEngine()
            builder = NewsCandidateBuilder()
            selector = CandidateSelector()
            while selected_candidate is None:
                raw_results = engine.search(discovery_request)
                candidates = builder.build(raw_results)
                if not candidates:
                    raise RuntimeError(
                        f"No news candidates found for: {discovery_request.query}"
                    )
                selected_candidate = selector.select(candidates)

            source_url = selected_candidate.url

        request = DirectSourceRequest(source_url=source_url)
        extractor = SourceExtractor()
        extracted = extractor.extract(request)

        evidence_builder = SourceEvidenceBuilder()
        evidence = evidence_builder.build(extracted)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Create run and write artifacts
    store = ProductionRunStore()
    run = None
    try:
        run = store.create(run_id)

        if selected_candidate is not None:
            store.write_candidates(run, candidates, selected_candidate)

        evidence_json = json.dumps(evidence.to_json_dict(), indent=2)
        run.source_evidence_path.write_text(evidence_json, encoding="utf-8")

        generator = StoryArtifactGenerator()
        artifacts = generator.generate(evidence)

        store.write_story_artifacts(run, artifacts)

        print(f"Production Run created: {run.directory}")
        print("Next Step: Review the draft script at:")
        print(f"  {run.script_path}")
        print("To approve the script, edit the file and change 'Status: draft' to 'Status: approved'.")

    except Exception as e:
        if run is not None and run.directory.exists():
            import shutil
            shutil.rmtree(run.directory)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
