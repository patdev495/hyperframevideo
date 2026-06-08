# Thin voiceover provider interface

The MVP will use HyperFrames local TTS for English narration, but the pipeline will call it through a thin voiceover provider interface. This avoids coupling script approval, transcript timing, and render orchestration to one TTS implementation, while keeping the initial implementation small enough to support future Vietnamese providers such as OpenAI, ElevenLabs, FPT.AI, Zalo AI, Viettel AI, or manual audio upload.
