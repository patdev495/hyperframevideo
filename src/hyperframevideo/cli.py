from __future__ import annotations

import argparse
import datetime
import json
import shutil
import sys

from hyperframevideo import __version__
from hyperframevideo.candidate_selector import CandidateSelector
from hyperframevideo.discovery_engine import DiscoveryEngine
from hyperframevideo.models import DirectSourceRequest, DiscoveryRequest, NewsCandidate
from hyperframevideo.news_candidate_builder import NewsCandidateBuilder
from hyperframevideo.production_runs import (
    ProductionRun,
    ProductionRunStore,
    VoiceoverManifestEntry,
)
from hyperframevideo.script_approval import ScriptApprovalGate
from hyperframevideo.script_scenes import (
    ScriptStoryboardError,
    ScriptStoryboardExtractor,
)
from hyperframevideo.storyboard_generator import StoryboardMarkdownGenerator
from hyperframevideo.storyboard_planning import StoryboardPlanner
from hyperframevideo.voiceover_timing import VoiceoverTimingError, VoiceoverTimingLoader
from hyperframevideo.source_evidence import SourceEvidenceBuilder
from hyperframevideo.source_extractor import SourceExtractor
from hyperframevideo.story_artifacts import StoryArtifactGenerator
from hyperframevideo.voiceover_segments import (
    VoiceoverNarrationError,
    VoiceoverNarrationExtractor,
)
from hyperframevideo.vieneu_voiceover import (
    VieNeuVoiceoverProvider,
    VoiceoverProviderError,
)


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
    parser.add_argument(
        "--voiceover",
        metavar="RUN_ID",
        help="Generate voiceover for an approved production run.",
    )
    parser.add_argument(
        "--storyboard",
        metavar="RUN_ID",
        help="Generate a storyboard for a production run with voiceover timing.",
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

    if args.storyboard:
        if args.url or args.discover or args.voiceover:
            parser.error("Provide --storyboard without a source URL, --discover, or --voiceover.")

        store = ProductionRunStore()
        run = ProductionRun(
            run_id=args.storyboard,
            directory=store.root / args.storyboard,
        )

        if run.storyboard_path.exists():
            print(
                f"Error: STORYBOARD.md already exists for Production Run: {args.storyboard}.",
                file=sys.stderr,
            )
            return 1

        try:
            script_markdown = run.script_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"Error: SCRIPT.md not found for Production Run: {args.storyboard}",
                file=sys.stderr,
            )
            return 1

        approval = ScriptApprovalGate().evaluate(script_markdown)
        if not approval.is_approved:
            print(f"Error: {approval.diagnostic}", file=sys.stderr)
            return 1

        if not run.voiceover_manifest_path.exists():
            print(
                f"Error: voiceover.json not found for Production Run: {args.storyboard}",
                file=sys.stderr,
            )
            return 1

        try:
            voiceover_json = run.voiceover_manifest_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"Error: voiceover.json not found for Production Run: {args.storyboard}",
                file=sys.stderr,
            )
            return 1

        try:
            scenes = ScriptStoryboardExtractor().extract(script_markdown)
        except ScriptStoryboardError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        try:
            timing_entries = VoiceoverTimingLoader().load(voiceover_json)
        except VoiceoverTimingError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        try:
            planned_scenes = StoryboardPlanner().plan(scenes, timing_entries)
        except Exception as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        markdown = StoryboardMarkdownGenerator().generate(
            planned_scenes,
            run_id=args.storyboard,
            visual_treatment="ai-modern",
        )

        store.write_storyboard(run, markdown)
        print(f"Storyboard written to: {run.storyboard_path}")
        print("Next Step: Review the storyboard and prepare for HyperFrames composition generation.")
        return 0

    if args.voiceover:
        if args.url or args.discover:
            parser.error("Provide --voiceover without a source URL or --discover.")

        store = ProductionRunStore()
        run = ProductionRun(
            run_id=args.voiceover,
            directory=store.root / args.voiceover,
        )
        script_path = run.script_path
        try:
            script_markdown = script_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"Error: SCRIPT.md not found for Production Run: {args.voiceover}",
                file=sys.stderr,
            )
            return 1

        approval = ScriptApprovalGate().evaluate(script_markdown)
        if not approval.is_approved:
            print(f"Error: {approval.diagnostic}", file=sys.stderr)
            return 1

        try:
            segments = VoiceoverNarrationExtractor().extract(script_markdown)
        except VoiceoverNarrationError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        if run.voiceover_manifest_path.exists() or (
            run.voiceover_audio_dir.exists()
            and any(run.voiceover_audio_dir.iterdir())
        ):
            print(
                f"Error: Voiceover artifacts already exist for Production Run: {args.voiceover}",
                file=sys.stderr,
            )
            return 1

        audio_dir = store.create_voiceover_audio_dir(run)
        try:
            outputs = VieNeuVoiceoverProvider().synthesize(segments, audio_dir=audio_dir)
        except VoiceoverProviderError as error:
            if audio_dir.exists() and not any(audio_dir.iterdir()):
                shutil.rmtree(audio_dir)
            print(f"Error: {error}", file=sys.stderr)
            return 1

        provider_name = outputs[0].provider_name
        store.write_voiceover_manifest(
            run,
            provider_name=provider_name,
            entries=[
                VoiceoverManifestEntry(
                    segment_id=output.segment_id,
                    order=output.order,
                    narration_text=output.narration_text,
                    audio_path=output.audio_path,
                    duration_seconds=output.duration_seconds,
                    warnings=output.warnings,
                )
                for output in outputs
            ],
        )

        print(f"Voiceover approved for Production Run: {args.voiceover}")
        print(f"Extracted voiceover segments: {len(segments)}")
        print(f"Voiceover manifest: {run.voiceover_manifest_path}")
        print("Next Step: Use voiceover.json for storyboard timing.")
        return 0

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
            shutil.rmtree(run.directory)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
