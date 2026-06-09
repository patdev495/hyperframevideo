from __future__ import annotations

from dataclasses import dataclass

from hyperframevideo.storyboard_planning import StoryboardScene
from hyperframevideo.treatment_config import TreatmentConfig


@dataclass(frozen=True, slots=True)
class CompositionGenerator:
    def generate(
        self,
        scenes: list[StoryboardScene],
        treatment: TreatmentConfig,
        *,
        run_id: str = "",
    ) -> str:
        lines: list[str] = []
        lines.append("<!DOCTYPE html>")
        lines.append('<html lang="en">')
        lines.append("<head>")
        lines.append("<meta charset='utf-8'>")
        lines.append("<style>")
        lines.append("  * { margin: 0; padding: 0; box-sizing: border-box; }")
        lines.append(f"  body {{ background: {treatment.background_color}; color: {treatment.text_color}; font-family: {treatment.font_family}; overflow: hidden; }}")
        lines.append(f"  #stage {{ width: 1080px; height: 1920px; position: relative; overflow: hidden; }}")
        lines.append(f"  .scene {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px; }}")
        lines.append(f"  .title {{ font-size: {treatment.title_font_size}; font-weight: 700; margin-bottom: 24px; color: {treatment.text_color}; text-align: center; }}")
        lines.append(f"  .body {{ font-size: {treatment.body_font_size}; font-weight: 400; color: {treatment.accent_color}; text-align: center; line-height: 1.5; }}")
        lines.append("</style>")
        lines.append("</head>")
        lines.append("<body>")

        lines.append(f'<div id="stage" data-composition-id="{run_id}" data-start="0" data-width="1080" data-height="1920">')

        for index, scene in enumerate(scenes):
            track = index
            lines.append(f'  <div class="scene" data-composition-id="{run_id}" data-start="{scene.start_time_seconds}" data-duration="{scene.duration_seconds}" data-track-index="{track}">')
            narration = scene.narration_text.replace("&", "&amp;").replace("<", "&lt;")
            on_screen = (scene.on_screen_text or "").replace("&", "&amp;").replace("<", "&lt;")
            if on_screen:
                lines.append(f'    <h2 class="title">{on_screen}</h2>')
            lines.append(f'    <p class="body">{narration}</p>')
            lines.append("  </div>")

            audio_path = scene.audio_path.replace("&", "&amp;").replace("<", "&lt;")
            lines.append(f'  <audio data-start="{scene.start_time_seconds}" data-duration="{scene.duration_seconds}" data-track-index="{track}" src="{audio_path}"></audio>')

        lines.append("</div>")

        lines.append('<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>')
        lines.append("<script>")
        lines.append("  const tl = gsap.timeline({ paused: true });")
        for index, scene in enumerate(scenes):
            lines.append(f"  tl.from('.scene:nth-child({index + 1})', {{ opacity: 0, y: {int(treatment.slide_up_duration * 100)}, duration: {treatment.fade_in_duration} }}, {scene.start_time_seconds});")
        lines.append("  window.__timelines = window.__timelines || {};")
        lines.append(f'  window.__timelines["{run_id}"] = tl;')
        lines.append("</script>")
        lines.append("</body>")
        lines.append("</html>")

        return "\n".join(lines)
