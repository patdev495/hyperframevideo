# Thin voiceover provider interface

The MVP will use a thin voiceover provider interface so script approval, transcript timing, and render orchestration are not coupled to one speech engine.

The first real provider target is VieNeu-TTS because it is Vietnamese-focused, local-first, available as a Python SDK, and licensed under Apache-2.0. The interface must still allow later providers such as HyperFrames local TTS, OpenAI, ElevenLabs, FPT.AI, Zalo AI, Viettel AI, or manual audio upload without changing the core orchestration logic.
