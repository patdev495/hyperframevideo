from __future__ import annotations

import argparse
import datetime
import json
import shutil
import subprocess
import sys
from importlib.resources import files as resource_files
from pathlib import Path

from hyperframevideo import __version__
from hyperframevideo.candidate_selector import CandidateSelector
from hyperframevideo.discovery_engine import DiscoveryEngine
from hyperframevideo.karaoke_captions import ApproximateKaraokeCaptionProvider
from hyperframevideo.models import DirectSourceRequest, DiscoveryRequest, NewsCandidate
from hyperframevideo.news_candidate_builder import NewsCandidateBuilder
from hyperframevideo.pipeline_orchestrator import (
    PipelineOrchestrator,
    PipelineRunRequest,
)
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
from hyperframevideo.composition_generator import CompositionGenerator
from hyperframevideo.treatment_config import TreatmentConfigError, TreatmentConfigLoader
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


def _visual_treatment_from_markdown(markdown: str, default: str = "tech-hype") -> str:
    for line in markdown.splitlines():
        if line.startswith("Visual Treatment:"):
            value = line.split(":", 1)[1].strip()
            return value or default
    return default


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
        "--list-treatments",
        action="store_true",
        help="List available Visual Treatments and exit.",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available TTS voices and exit.",
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
        "--voice",
        default=None,
        help="Voice name for TTS. Use --list-voices to see available options.",
    )
    parser.add_argument(
        "--emotion",
        default="natural",
        help="Emotion for TTS voice (default: natural).",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed factor (0.5-2.0, default: 1.0).",
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
    parser.add_argument(
        "--compose",
        metavar="RUN_ID",
        help="Generate a HyperFrames composition from a storyboard.",
    )
    parser.add_argument(
        "--render",
        metavar="RUN_ID",
        help="Render a composition to MP4 using HyperFrames.",
    )
    return parser


def build_run_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyperframe-video run",
        description="Run the orchestrated News-to-Video pipeline.",
    )
    parser.add_argument("--url", required=True, help="The source URL to process.")
    parser.add_argument(
        "--run-id",
        required=True,
        help="The ID for the production run to create or resume.",
    )
    parser.add_argument(
        "--script-provider",
        default="deepseek",
        choices=("deepseek",),
        help="The Source-Grounded Script drafting provider.",
    )
    parser.add_argument(
        "--language",
        default="en",
        choices=("en", "vi"),
        help="The language code for generated SCRIPT.md content.",
    )
    parser.add_argument(
        "--script-model",
        help="Override the script provider model.",
    )
    parser.add_argument(
        "--auto-approve-script",
        action="store_true",
        help="Approve a newly drafted script and continue through composition.",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Render output.mp4 after composition.",
    )
    parser.add_argument(
        "--treatment",
        default=None,
        help=(
            "Visual Treatment to use (default: tech-hype). "
            "Use --list-treatments to see available options."
        ),
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="Voice name for TTS. Use --list-voices to see available options.",
    )
    parser.add_argument(
        "--emotion",
        default="natural",
        help="Emotion for TTS voice (default: natural).",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speech speed factor (0.5-2.0, default: 1.0).",
    )
    parser.add_argument(
        "--progress-format",
        choices=("text", "jsonl"),
        default="text",
        help="How to print live progress.",
    )
    return parser


def _run_orchestrated(argv: list[str]) -> int:
    parser = build_run_parser()
    args = parser.parse_args(argv)

    def write_progress(line: str) -> None:
        print(line)

    return PipelineOrchestrator().run(
        PipelineRunRequest(
            url=args.url,
            run_id=args.run_id,
            language=args.language,
            script_provider=args.script_provider,
            script_model=args.script_model,
            auto_approve_script=args.auto_approve_script,
            render=args.render,
            progress_format=args.progress_format,
            progress_writer=write_progress,
            visual_treatment=args.treatment or "tech-hype",
            voice_name=args.voice,
            emotion=args.emotion,
            speed=args.speed,
        )
    )


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "run":
        return _run_orchestrated(argv[1:])

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"hyperframevideo {__version__}")
        return 0

    if args.list_treatments:
        treatments_path = (
            resource_files("hyperframevideo") / "treatments.json"
        )
        names = TreatmentConfigLoader().list_names(Path(str(treatments_path)))
        if not names:
            print("No treatments found.", file=sys.stderr)
            return 1
        print("Available Visual Treatments:")
        for name in names:
            print(f"  - {name}")
        return 0

    if args.list_voices:
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        try:
            from vieneu import Vieneu
            tts = Vieneu(mode="standard")
            voices = tts.list_preset_voices()
            print("Available TTS Voices:")
            for display_name, voice_name in voices:
                print(f"  {voice_name:20s} {display_name}")
        except ImportError:
            print(
                "VieNeu SDK is not installed. "
                "Install it before listing voices.",
                file=sys.stderr,
            )
            return 1
        return 0

    if args.url and args.discover:
        parser.error("Provide either a source URL or --discover, not both.")

    if args.storyboard:
        if args.url or args.discover or args.voiceover or args.compose:
            parser.error("Provide --storyboard without a source URL, --discover, --voiceover, or --compose.")

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
            visual_treatment=_visual_treatment_from_markdown(script_markdown),
        )

        store.write_storyboard(run, markdown)
        print(f"Storyboard written to: {run.storyboard_path}")
        print("Next Step: Review the storyboard and prepare for HyperFrames composition generation.")
        return 0

    if args.compose:
        store = ProductionRunStore()
        run = ProductionRun(
            run_id=args.compose,
            directory=store.root / args.compose,
        )

        if run.composition_dir.exists():
            print(
                f"Error: composition/ already exists for Production Run: {args.compose}.",
                file=sys.stderr,
            )
            return 1

        if not run.storyboard_path.exists():
            print(
                f"Error: STORYBOARD.md not found for Production Run: {args.compose}.",
                file=sys.stderr,
            )
            return 1

        try:
            script_markdown = run.script_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"Error: SCRIPT.md not found for Production Run: {args.compose}",
                file=sys.stderr,
            )
            return 1

        approval = ScriptApprovalGate().evaluate(script_markdown)
        if not approval.is_approved:
            print(f"Error: {approval.diagnostic}", file=sys.stderr)
            return 1

        if not run.voiceover_manifest_path.exists():
            print(
                f"Error: voiceover.json not found for Production Run: {args.compose}",
                file=sys.stderr,
            )
            return 1

        try:
            voiceover_json = run.voiceover_manifest_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(
                f"Error: voiceover.json not found for Production Run: {args.compose}",
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

        # Read visual treatment from STORYBOARD.md header
        storyboard_content = run.storyboard_path.read_text(encoding="utf-8")
        visual_treatment = _visual_treatment_from_markdown(storyboard_content)

        # Load treatment config
        treatments_path = (
            resource_files("hyperframevideo") / "treatments.json"
        )
        try:
            treatment = TreatmentConfigLoader().load(
                Path(str(treatments_path)), visual_treatment
            )
        except TreatmentConfigError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1

        karaoke_captions = store.read_karaoke_captions(run)
        if visual_treatment == "premium-news" and karaoke_captions is None:
            karaoke_captions = ApproximateKaraokeCaptionProvider().generate_manifest(
                tuple(
                    (
                        entry.segment_id,
                        entry.narration_text,
                        entry.duration_seconds,
                    )
                    for entry in timing_entries
                )
            )
            store.write_karaoke_captions(run, karaoke_captions)

        # Generate composition HTML
        html = CompositionGenerator().generate(
            planned_scenes,
            treatment,
            run_id=args.compose,
            karaoke_captions=karaoke_captions,
        )
        store.write_composition_html(run, html)

        # Copy audio files to composition/voiceover/
        audio_dest = run.composition_dir / "voiceover"
        audio_dest.mkdir(parents=True, exist_ok=True)
        for scene in planned_scenes:
            audio_name = Path(scene.audio_path).name
            src = run.voiceover_audio_dir / audio_name
            if src.exists():
                shutil.copy2(src, audio_dest / audio_name)

        print(f"Composition written to: {run.composition_dir / 'index.html'}")
        print("Next Step: Render the composition with hyperframe-video --render.")
        return 0

    if args.render:
        if args.url or args.discover or args.voiceover or args.storyboard or args.compose:
            parser.error("Provide --render without other source, --voiceover, --storyboard, or --compose flags.")

        store = ProductionRunStore()
        run = ProductionRun(
            run_id=args.render,
            directory=store.root / args.render,
        )

        if not run.composition_dir.exists():
            print(
                f"Error: composition/ not found for Production Run: {args.render}. "
                "Run --compose first.",
                file=sys.stderr,
            )
            return 1

        if run.render_output_path.exists():
            print(
                f"Error: output.mp4 already exists for Production Run: {args.render}.",
                file=sys.stderr,
            )
            return 1

        # Check system requirements
        missing: list[str] = []
        for tool in ("node", "npx", "ffmpeg"):
            if shutil.which(tool) is None:
                missing.append(tool)
        if missing:
            print(
                f"Error: Missing required tools: {', '.join(missing)}. "
                "Please install them before rendering.",
                file=sys.stderr,
            )
            return 1

        # Run npx hyperframes render in composition directory
        # Use shell=True on Windows so .cmd files (npx.cmd) are resolved
        result = subprocess.run(
            "npx hyperframes render",
            cwd=str(run.composition_dir),
            capture_output=True,
            text=True,
            shell=True,
        )

        if result.returncode != 0:
            print(
                f"Error: HyperFrames render failed:\n{result.stderr.strip()}",
                file=sys.stderr,
            )
            return 1

        # Copy generated MP4 to run directory
        # HyperFrames outputs to renders/composition_<timestamp>.mp4 by default
        renders_dir = run.composition_dir / "renders"
        generated_mp4: Path | None = None
        if renders_dir.is_dir():
            mp4_files = sorted(renders_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
            if mp4_files:
                generated_mp4 = mp4_files[0]

        if generated_mp4 is not None and generated_mp4.exists():
            shutil.copy2(generated_mp4, run.render_output_path)
            print(f"Video rendered to: {run.render_output_path}")
            print("Next Step: View the video or run the pipeline for another source.")
        else:
            print(
                "Error: HyperFrames render completed but output.mp4 was not found.",
                file=sys.stderr,
            )
            return 1
        return 0

    if args.voiceover:
        if args.url or args.discover or args.compose:
            parser.error("Provide --voiceover without a source URL, --discover, or --compose.")

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
            outputs = VieNeuVoiceoverProvider(
                voice_name=args.voice,
                emotion=args.emotion,
                speed=args.speed,
            ).synthesize(segments, audio_dir=audio_dir)
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
