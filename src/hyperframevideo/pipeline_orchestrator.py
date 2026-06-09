from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from importlib.resources import files as resource_files
from pathlib import Path
from typing import Callable

from hyperframevideo.composition_generator import CompositionGenerator
from hyperframevideo.deepseek_script_provider import (
    DeepSeekScriptDraftingProvider,
    ScriptDraftingProviderError,
)
from hyperframevideo.karaoke_captions import ApproximateKaraokeCaptionProvider
from hyperframevideo.markdown_fields import partition_markdown_field
from hyperframevideo.models import DirectSourceRequest
from hyperframevideo.pipeline_progress import (
    PipelineProgressEvent,
    PipelineProgressLog,
    format_progress_jsonl,
    format_progress_text,
)
from hyperframevideo.production_runs import (
    ProductionRun,
    ProductionRunStore,
    VoiceoverManifestEntry,
)
from hyperframevideo.script_approval import ScriptApprovalGate
from hyperframevideo.script_drafting import (
    ScriptDraftingPrompt,
    ScriptDraftingProvider,
)
from hyperframevideo.script_scenes import ScriptStoryboardExtractor
from hyperframevideo.source_evidence import SourceEvidence, SourceEvidenceBuilder
from hyperframevideo.source_extractor import SourceExtractor
from hyperframevideo.story_artifacts import StoryArtifactGenerator
from hyperframevideo.storyboard_generator import StoryboardMarkdownGenerator
from hyperframevideo.storyboard_planning import StoryboardPlanner
from hyperframevideo.treatment_config import TreatmentConfigLoader
from hyperframevideo.vieneu_voiceover import VieNeuVoiceoverProvider
from hyperframevideo.voiceover_segments import VoiceoverNarrationExtractor
from hyperframevideo.voiceover_timing import VoiceoverTimingLoader


ProgressWriter = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class PipelineRunRequest:
    url: str
    run_id: str
    language: str = "en"
    script_provider: str = "deepseek"
    script_model: str | None = None
    auto_approve_script: bool = False
    render: bool = False
    progress_format: str = "text"
    progress_writer: ProgressWriter | None = None
    visual_treatment: str = "tech-hype"


@dataclass(slots=True)
class PipelineOrchestrator:
    runs_root: Path = Path(".runs")
    source_extractor: object | None = None
    script_provider: ScriptDraftingProvider | None = None
    voiceover_provider: object | None = None
    tool_locator: Callable[[str], str | None] = shutil.which
    process_runner: Callable[..., subprocess.CompletedProcess] | None = None

    def run(self, request: PipelineRunRequest) -> int:
        store = ProductionRunStore(root=self.runs_root)
        run = self._get_or_create_run(store, request.run_id)
        progress = _ProgressReporter(run, request)

        try:
            evidence = self._ensure_source_evidence(store, run, request, progress)
            self._ensure_selected_story(store, run, evidence)
            script_existed = run.script_path.exists()
            self._ensure_script(run, evidence, request, progress)
            approval = ScriptApprovalGate().evaluate(
                run.script_path.read_text(encoding="utf-8")
            )

            if not approval.is_approved:
                if request.auto_approve_script and not script_existed:
                    self._approve_script(run)
                    progress.emit(
                        "script_approval",
                        "completed",
                        "Auto-approved drafted SCRIPT.md",
                        artifact_path=run.script_path,
                    )
                else:
                    progress.emit(
                        "script_approval",
                        "waiting_for_approval",
                        "Review SCRIPT.md and change Status to approved",
                        artifact_path=run.script_path,
                    )
                    return 0

            if not request.auto_approve_script and not ScriptApprovalGate().evaluate(
                run.script_path.read_text(encoding="utf-8")
            ).is_approved:
                return 0

            self._ensure_voiceover(store, run, progress)
            self._ensure_storyboard(store, run, progress)
            self._ensure_composition(store, run, progress)
            if request.render:
                return self._ensure_render(run, progress)
            return 0
        except Exception as error:
            progress.emit(
                "pipeline",
                "failed",
                "Pipeline failed",
                error=str(error),
            )
            return 1

    def _get_or_create_run(self, store: ProductionRunStore, run_id: str) -> ProductionRun:
        run = ProductionRun(run_id=run_id, directory=store.root / run_id)
        run.directory.mkdir(parents=True, exist_ok=True)
        return run

    def _ensure_source_evidence(
        self,
        store: ProductionRunStore,
        run: ProductionRun,
        request: PipelineRunRequest,
        progress: "_ProgressReporter",
    ) -> SourceEvidence:
        if run.source_evidence_path.exists():
            progress.emit(
                "extract_source",
                "skipped",
                "Using existing source evidence",
                artifact_path=run.source_evidence_path,
            )
            return _read_source_evidence(run.source_evidence_path)

        progress.emit("extract_source", "started", "Extracting source evidence")
        extractor = self.source_extractor or SourceExtractor()
        extracted = extractor.extract(DirectSourceRequest(source_url=request.url))
        evidence = SourceEvidenceBuilder().build(extracted)
        run.source_evidence_path.write_text(
            json.dumps(evidence.to_json_dict(), indent=2), encoding="utf-8"
        )
        progress.emit(
            "extract_source",
            "completed",
            "Wrote source evidence",
            artifact_path=run.source_evidence_path,
        )
        return evidence

    def _ensure_selected_story(
        self, store: ProductionRunStore, run: ProductionRun, evidence: SourceEvidence
    ) -> None:
        if run.selected_story_path.exists():
            return
        artifacts = StoryArtifactGenerator().generate(evidence)
        run.selected_story_path.write_text(
            artifacts.selected_story_markdown, encoding="utf-8"
        )

    def _ensure_script(
        self,
        run: ProductionRun,
        evidence: SourceEvidence,
        request: PipelineRunRequest,
        progress: "_ProgressReporter",
    ) -> None:
        if run.script_path.exists():
            progress.emit(
                "draft_script",
                "skipped",
                "Using existing SCRIPT.md",
                artifact_path=run.script_path,
            )
            return

        progress.emit("draft_script", "started", "Drafting SCRIPT.md")
        provider = self.script_provider or self._resolve_script_provider(request)
        result = provider.draft_script(
            evidence, _load_script_drafting_prompt(language=request.language)
        )
        script = _apply_visual_treatment(
            result.script_markdown, request.visual_treatment
        )
        run.script_path.write_text(script, encoding="utf-8")
        progress.emit(
            "draft_script",
            "completed",
            "Wrote SCRIPT.md",
            artifact_path=run.script_path,
            provider_name=result.provider_name,
            model=result.model,
        )

    def _resolve_script_provider(
        self, request: PipelineRunRequest
    ) -> ScriptDraftingProvider:
        if request.script_provider != "deepseek":
            raise ScriptDraftingProviderError(
                f"Unsupported script provider: {request.script_provider}"
            )
        return DeepSeekScriptDraftingProvider.from_environment(
            model_override=request.script_model
        )

    def _approve_script(self, run: ProductionRun) -> None:
        script = run.script_path.read_text(encoding="utf-8")
        lines = script.splitlines()
        for index, line in enumerate(lines):
            label, separator, _value = partition_markdown_field(line)
            if separator and label.strip().lower() == "status":
                lines[index] = "Status: approved"
                run.script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                return

    def _ensure_voiceover(
        self, store: ProductionRunStore, run: ProductionRun, progress: "_ProgressReporter"
    ) -> None:
        if run.voiceover_manifest_path.exists():
            progress.emit(
                "voiceover",
                "skipped",
                "Using existing voiceover manifest",
                artifact_path=run.voiceover_manifest_path,
            )
            return

        progress.emit("voiceover", "started", "Generating voiceover")
        script = run.script_path.read_text(encoding="utf-8")
        segments = VoiceoverNarrationExtractor().extract(script)
        audio_dir = store.create_voiceover_audio_dir(run)
        outputs = (self.voiceover_provider or VieNeuVoiceoverProvider()).synthesize(
            segments, audio_dir=audio_dir
        )
        store.write_voiceover_manifest(
            run,
            provider_name=outputs[0].provider_name if outputs else "unknown",
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
        progress.emit(
            "voiceover",
            "completed",
            "Wrote voiceover manifest",
            artifact_path=run.voiceover_manifest_path,
        )

    def _ensure_storyboard(
        self, store: ProductionRunStore, run: ProductionRun, progress: "_ProgressReporter"
    ) -> None:
        if run.storyboard_path.exists():
            progress.emit(
                "storyboard",
                "skipped",
                "Using existing STORYBOARD.md",
                artifact_path=run.storyboard_path,
            )
            return

        progress.emit("storyboard", "started", "Generating storyboard")
        script = run.script_path.read_text(encoding="utf-8")
        voiceover_json = run.voiceover_manifest_path.read_text(encoding="utf-8")
        scenes = ScriptStoryboardExtractor().extract(script)
        timing_entries = VoiceoverTimingLoader().load(voiceover_json)
        planned_scenes = StoryboardPlanner().plan(scenes, timing_entries)
        markdown = StoryboardMarkdownGenerator().generate(
            planned_scenes,
            run_id=run.run_id,
            visual_treatment=_visual_treatment_from_markdown(script),
        )
        store.write_storyboard(run, markdown)
        progress.emit(
            "storyboard",
            "completed",
            "Wrote STORYBOARD.md",
            artifact_path=run.storyboard_path,
        )

    def _ensure_composition(
        self, store: ProductionRunStore, run: ProductionRun, progress: "_ProgressReporter"
    ) -> None:
        if run.composition_dir.exists():
            progress.emit(
                "compose",
                "skipped",
                "Using existing composition",
                artifact_path=run.composition_dir,
            )
            return

        progress.emit("compose", "started", "Generating composition")
        script = run.script_path.read_text(encoding="utf-8")
        voiceover_json = run.voiceover_manifest_path.read_text(encoding="utf-8")
        storyboard = run.storyboard_path.read_text(encoding="utf-8")
        scenes = ScriptStoryboardExtractor().extract(script)
        timing_entries = VoiceoverTimingLoader().load(voiceover_json)
        planned_scenes = StoryboardPlanner().plan(scenes, timing_entries)
        visual_treatment = _visual_treatment_from_markdown(storyboard)
        treatment_path = resource_files("hyperframevideo") / "treatments.json"
        treatment = TreatmentConfigLoader().load(Path(str(treatment_path)), visual_treatment)
        karaoke_captions = store.read_karaoke_captions(run)
        if visual_treatment == "premium-news" and karaoke_captions is None:
            karaoke_captions = ApproximateKaraokeCaptionProvider().generate_manifest(
                tuple(
                    (entry.segment_id, entry.narration_text, entry.duration_seconds)
                    for entry in timing_entries
                )
            )
            store.write_karaoke_captions(run, karaoke_captions)
        html = CompositionGenerator().generate(
            planned_scenes,
            treatment,
            run_id=run.run_id,
            karaoke_captions=karaoke_captions,
        )
        store.write_composition_html(run, html)
        audio_dest = run.composition_dir / "voiceover"
        audio_dest.mkdir(parents=True, exist_ok=True)
        for scene in planned_scenes:
            source = run.voiceover_audio_dir / Path(scene.audio_path).name
            if source.exists():
                shutil.copy2(source, audio_dest / source.name)
        progress.emit(
            "compose",
            "completed",
            "Wrote composition",
            artifact_path=run.composition_dir,
        )

    def _ensure_render(self, run: ProductionRun, progress: "_ProgressReporter") -> int:
        if run.render_output_path.exists():
            progress.emit(
                "render",
                "skipped",
                "Using existing rendered video",
                artifact_path=run.render_output_path,
            )
            return 0
        missing = [tool for tool in ("node", "npx", "ffmpeg") if self.tool_locator(tool) is None]
        if missing:
            progress.emit(
                "render",
                "failed",
                "Render requirements missing",
                error=f"Missing required tools: {', '.join(missing)}",
            )
            return 1

        progress.emit("render", "started", "Rendering composition")
        runner = self.process_runner or subprocess.run
        result = runner(
            "npx hyperframes render",
            cwd=str(run.composition_dir),
            capture_output=True,
            text=True,
            shell=True,
        )
        if result.returncode != 0:
            progress.emit(
                "render",
                "failed",
                "HyperFrames render failed",
                error=(result.stderr or "").strip(),
            )
            return 1
        renders_dir = run.composition_dir / "renders"
        mp4_files = (
            sorted(renders_dir.glob("*.mp4"), key=lambda path: path.stat().st_mtime, reverse=True)
            if renders_dir.is_dir()
            else []
        )
        if not mp4_files:
            progress.emit(
                "render",
                "failed",
                "HyperFrames render completed without MP4 output",
                error="output.mp4 was not found",
            )
            return 1
        shutil.copy2(mp4_files[0], run.render_output_path)
        progress.emit(
            "render",
            "completed",
            "Wrote rendered video",
            artifact_path=run.render_output_path,
        )
        return 0


@dataclass(slots=True)
class _ProgressReporter:
    run: ProductionRun
    request: PipelineRunRequest
    log: PipelineProgressLog = field(init=False)

    def __post_init__(self) -> None:
        self.log = PipelineProgressLog(self.run.progress_log_path)

    def emit(
        self,
        phase: str,
        status: str,
        message: str = "",
        *,
        artifact_path: Path | None = None,
        provider_name: str | None = None,
        model: str | None = None,
        error: str | None = None,
    ) -> None:
        event = PipelineProgressEvent(
            phase=phase,
            status=status,
            message=message,
            artifact_path=artifact_path,
            provider_name=provider_name,
            model=model,
            error=error,
        )
        self.log.append(event)
        if self.request.progress_writer is None:
            return
        formatter = (
            format_progress_jsonl
            if self.request.progress_format == "jsonl"
            else format_progress_text
        )
        self.request.progress_writer(formatter(event))


def _read_source_evidence(path: Path) -> SourceEvidence:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SourceEvidence(
        url=payload["url"],
        title=payload["title"],
        source_name=payload.get("source_name"),
        published_at=payload.get("published_at"),
        extracted_text=payload["extracted_text"],
        extraction_method=payload["extraction_method"],
        warnings=tuple(payload.get("warnings", ())),
    )


def _load_script_drafting_prompt(*, language: str) -> ScriptDraftingPrompt:
    prompt_name = "script-drafting.vi.md" if language == "vi" else "script-drafting.md"
    prompt_path = Path("docs") / "prompts" / prompt_name
    if prompt_path.exists():
        prompt_text = prompt_path.read_text(encoding="utf-8")
    else:
        fallback = Path("docs") / "prompts" / "script-drafting.md"
        if fallback.exists():
            prompt_text = fallback.read_text(encoding="utf-8")
        else:
            prompt_text = (
                "Produce SCRIPT.md only as a Source-Grounded Script "
                "from the Source Evidence."
            )
    language_override = (
        f"\nLanguage: {language}\n"
        f"All content must be written in {_language_name(language)}.\n"
    )
    return ScriptDraftingPrompt(f"{prompt_text}\n\n{language_override}")


def _language_name(language: str) -> str:
    return {
        "en": "English",
        "vi": "Vietnamese",
    }.get(language, language)


def _visual_treatment_from_markdown(markdown: str, default: str = "tech-hype") -> str:
    for line in markdown.splitlines():
        if line.startswith("Visual Treatment:"):
            value = line.split(":", 1)[1].strip()
            return value or default
    return default


def _apply_visual_treatment(markdown: str, treatment: str) -> str:
    """Overwrite the Visual Treatment header line in a SCRIPT.md / STORYBOARD.md."""
    lines = markdown.splitlines()
    for i, line in enumerate(lines):
        label, separator, _value = partition_markdown_field(line)
        if separator and label.strip().lower() == "visual treatment":
            lines[i] = f"Visual Treatment: {treatment}"
            return "\n".join(lines)
    return markdown
