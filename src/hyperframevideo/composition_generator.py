from __future__ import annotations

import json
from html import escape
from dataclasses import dataclass

from hyperframevideo.karaoke_captions import KaraokeCaptionManifest
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
        karaoke_captions: KaraokeCaptionManifest | None = None,
    ) -> str:
        if treatment.name == "premium-news":
            return self._generate_premium_news(
                scenes, treatment, run_id=run_id, karaoke_captions=karaoke_captions
            )

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
            lines.append(f'  <div class="clip scene" data-composition-id="{run_id}" data-start="{scene.start_time_seconds}" data-duration="{scene.duration_seconds}" data-track-index="{track}">')
            narration = scene.narration_text.replace("&", "&amp;").replace("<", "&lt;")
            on_screen = (scene.on_screen_text or "").replace("&", "&amp;").replace("<", "&lt;")
            if on_screen:
                lines.append(f'    <h2 class="title">{on_screen}</h2>')
            lines.append(f'    <p class="body">{narration}</p>')
            lines.append("  </div>")

            audio_path = scene.audio_path.replace("&", "&amp;").replace("<", "&lt;")
            audio_track = len(scenes) + index
            lines.append(f'  <audio id="audio-{scene.segment_id}" data-start="{scene.start_time_seconds}" data-duration="{scene.duration_seconds}" data-track-index="{audio_track}" src="{audio_path}"></audio>')

        lines.append("</div>")

        lines.append('<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>')
        lines.append("<script>")
        lines.append("  const tl = gsap.timeline({ paused: true });")
        for index, scene in enumerate(scenes):
            lines.append(f"  tl.from('.scene:nth-of-type({index + 1})', {{ opacity: 0, y: {int(treatment.slide_up_duration * 100)}, duration: {treatment.fade_in_duration} }}, {scene.start_time_seconds});")
        lines.append("  window.__timelines = window.__timelines || {};")
        lines.append(f'  window.__timelines["{run_id}"] = tl;')
        lines.append("</script>")
        lines.append("</body>")
        lines.append("</html>")

        return "\n".join(lines)

    def _generate_premium_news(
        self,
        scenes: list[StoryboardScene],
        treatment: TreatmentConfig,
        *,
        run_id: str,
        karaoke_captions: KaraokeCaptionManifest | None,
    ) -> str:
        captions_by_segment = {
            segment.segment_id: segment
            for segment in (karaoke_captions.segments if karaoke_captions else ())
        }
        lines: list[str] = [
            "<!DOCTYPE html>",
            '<html lang="en">',
            "<head>",
            "<meta charset='utf-8'>",
            "<style>",
            "  * { margin: 0; padding: 0; box-sizing: border-box; }",
            f"  body {{ background: {treatment.background_color}; color: {treatment.text_color}; font-family: {treatment.font_family}; overflow: hidden; }}",
            "  #stage { width: 1080px; height: 1920px; position: relative; overflow: hidden; background: #050816; }",
            "  .premium-bg-layer { position: absolute; inset: -10%; pointer-events: none; }",
            "  .premium-bg-layer.mesh { background: radial-gradient(circle at 20% 20%, rgba(56,189,248,.32), transparent 28%), radial-gradient(circle at 78% 12%, rgba(99,102,241,.28), transparent 30%), radial-gradient(circle at 50% 88%, rgba(20,184,166,.2), transparent 30%); filter: blur(2px); }",
            "  .premium-bg-layer.grid { background-image: linear-gradient(rgba(255,255,255,.06) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.06) 1px, transparent 1px); background-size: 54px 54px; opacity: .38; transform: perspective(700px) rotateX(58deg) translateY(280px); }",
            "  .premium-bg-layer.vignette { inset: 0; background: radial-gradient(circle at 50% 44%, transparent 36%, rgba(0,0,0,.72) 100%); }",
            "  .scene { position: absolute; inset: 0; display: grid; grid-template-rows: 1fr auto 1fr; padding: 112px 82px; opacity: 0; }",
            "  .premium-transition { position: absolute; inset: 0; background: linear-gradient(120deg, transparent, rgba(56,189,248,.28), transparent); transform: translateX(-120%); pointer-events: none; }",
            "  .scene-shell { align-self: center; display: grid; gap: 42px; }",
            f"  .eyebrow {{ color: {treatment.accent_color}; font-size: 30px; font-weight: 800; text-transform: uppercase; letter-spacing: 0; }}",
            f"  .title {{ color: {treatment.text_color}; font-size: {treatment.title_font_size}; line-height: 1.02; font-weight: 900; text-wrap: balance; }}",
            "  .title-accent { display: inline-block; padding: 0 14px; background: rgba(56,189,248,.16); border-left: 6px solid currentColor; }",
            "  .karaoke-caption { align-self: end; min-height: 190px; position: relative; padding: 30px 34px; border: 1px solid rgba(255,255,255,.16); background: rgba(5,8,22,.64); box-shadow: 0 24px 80px rgba(0,0,0,.34); backdrop-filter: blur(18px); overflow: hidden; }",
            "  .caption-window { position: absolute; inset: 30px 34px; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; opacity: 0; transform: translateY(16px); }",
            f"  .caption-token {{ font-size: {treatment.body_font_size}; line-height: 1.15; font-weight: 800; color: rgba(248,250,252,.42); transform: translateY(10px); opacity: .35; }}",
            f"  .caption-token.active-word {{ color: {treatment.accent_color}; text-shadow: 0 0 26px rgba(56,189,248,.54); opacity: 1; transform: translateY(0) scale(1.06); }}",
            "</style>",
            "</head>",
            "<body>",
            f'<div id="stage" data-composition-id="{escape(run_id)}" data-start="0" data-width="1080" data-height="1920" data-visual-treatment="premium-news">',
            '  <div class="premium-bg-layer mesh"></div>',
            '  <div class="premium-bg-layer grid"></div>',
            '  <div class="premium-bg-layer vignette"></div>',
        ]

        for index, scene in enumerate(scenes):
            track = index
            title = escape(scene.on_screen_text or f"Scene {scene.order}")
            lines.append(f'  <section class="clip scene premium-scene" data-composition-id="{escape(run_id)}" data-start="{scene.start_time_seconds}" data-duration="{scene.duration_seconds}" data-track-index="{track}">')
            lines.append('    <div class="premium-transition"></div>')
            lines.append('    <div></div>')
            lines.append('    <div class="scene-shell">')
            lines.append(f'      <div class="eyebrow">Scene {scene.order:02d}</div>')
            lines.append(f'      <h2 class="title"><span class="title-accent">{title}</span></h2>')
            lines.append('    </div>')
            lines.append('    <div class="karaoke-caption" data-caption-segment="' + escape(scene.segment_id) + '">')
            caption_segment = captions_by_segment.get(scene.segment_id)
            if caption_segment is not None:
                for window_index, window in enumerate(
                    caption_segment.phrase_windows(max_tokens=5), start=1
                ):
                    lines.append(
                        f'      <div class="caption-window" data-window-order="{window_index}">'
                    )
                    for token in window:
                        lines.append(
                            f'        <span class="caption-token" data-segment-id="{escape(scene.segment_id)}" data-token-order="{token.order}" '
                            f'data-token-start="{token.start_seconds}" data-token-end="{token.end_seconds}">{escape(token.text)}</span>'
                        )
                    lines.append("      </div>")
            lines.append("    </div>")
            lines.append("  </section>")

            audio_path = escape(scene.audio_path)
            audio_track = len(scenes) + index
            lines.append(f'  <audio id="audio-{escape(scene.segment_id)}" data-start="{scene.start_time_seconds}" data-duration="{scene.duration_seconds}" data-track-index="{audio_track}" src="{audio_path}"></audio>')

        caption_payload = json.dumps(
            karaoke_captions.to_json_dict() if karaoke_captions else {},
            ensure_ascii=False,
        )
        lines.extend(
            [
                "</div>",
                '<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>',
                "<script>",
                f"  window.__karaokeCaptions = {caption_payload};",
                "  const tl = gsap.timeline({ paused: true });",
            ]
        )
        for index, scene in enumerate(scenes):
            lines.append(f"  tl.to('.scene:nth-of-type({index + 1})', {{ opacity: 1, duration: {treatment.fade_in_duration} }}, {scene.start_time_seconds});")
            lines.append(f"  tl.from('.scene:nth-of-type({index + 1}) .scene-shell', {{ y: 90, filter: 'blur(18px)', duration: {treatment.slide_up_duration} }}, {scene.start_time_seconds});")
            lines.append(f"  tl.to('.scene:nth-of-type({index + 1}) .premium-transition', {{ x: '120%', duration: 0.72 }}, {scene.start_time_seconds});")
            caption_segment = captions_by_segment.get(scene.segment_id)
            if caption_segment is not None:
                for window_index, window in enumerate(
                    caption_segment.phrase_windows(max_tokens=5), start=1
                ):
                    window_start = scene.start_time_seconds + window[0].start_seconds
                    window_end = scene.start_time_seconds + window[-1].end_seconds
                    selector = f".scene:nth-of-type({index + 1}) .caption-window:nth-child({window_index})"
                    lines.append(f"  tl.to({_js_string(selector)}, {{ opacity: 1, y: 0, duration: 0.18 }}, {window_start});")
                    lines.append(f"  tl.to({_js_string(selector)}, {{ opacity: 0, y: -14, duration: 0.16 }}, {window_end});")
                for token in caption_segment.tokens:
                    token_selector = f".scene:nth-of-type({index + 1}) [data-token-order='{token.order}']"
                    token_start = scene.start_time_seconds + token.start_seconds
                    token_end = scene.start_time_seconds + token.end_seconds
                    lines.append(f"  tl.set({_js_string(token_selector)}, {{ className: 'caption-token active-word' }}, {token_start});")
                    lines.append(f"  tl.set({_js_string(token_selector)}, {{ className: 'caption-token' }}, {token_end});")
            scene_selector = f".scene:nth-of-type({index + 1})"
            scene_end = scene.start_time_seconds + scene.duration_seconds
            lines.append(f"  tl.to({_js_string(scene_selector)}, {{ opacity: 0, duration: 0.25 }}, {scene_end - 0.25});")
            lines.append(f"  tl.set({_js_string(scene_selector)}, {{ opacity: 0 }}, {scene_end});")
        lines.extend(
            [
                "  window.__timelines = window.__timelines || {};",
                f'  window.__timelines["{escape(run_id)}"] = tl;',
                "</script>",
                "</body>",
                "</html>",
            ]
        )
        return "\n".join(lines)


def _js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)
