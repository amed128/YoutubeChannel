"""
Sub-agent: Generates voiceover audio from the script narration.
Priority:
  1. User-provided audio file path (--audio flag) — used as-is.
  2. edge-tts — free Microsoft Azure neural voices, runs locally, no API key.
"""

import asyncio
from pathlib import Path

import edge_tts

# Good neutral Spanish voices (no regional accent preference):
# es-MX-JorgeNeural    — Mexican Spanish, male
# es-ES-AlvaroNeural   — Spain Spanish, male
# es-CO-GonzaloNeural  — Colombian Spanish, male
VOICE = "es-MX-JorgeNeural"


class VoiceoverAgent:
    """Generates or passes through the audio track for the video."""

    def run(
        self,
        script: dict,
        output_dir: Path,
        provided_audio: str | None = None,
    ) -> Path:
        if provided_audio:
            src = Path(provided_audio)
            if not src.exists():
                raise FileNotFoundError(f"Provided audio file not found: {src}")
            print(f"[Voiceover] Using provided audio: {src}")
            return src

        print(f"[Voiceover] Synthesizing speech with edge-tts (voice: {VOICE})...")
        output_dir.mkdir(parents=True, exist_ok=True)
        full_narration = " ".join(s["narration"] for s in script["scenes"])
        audio_path = output_dir / "voiceover.mp3"

        asyncio.run(self._synthesize(full_narration, audio_path))
        print(f"[Voiceover] Audio saved → {audio_path}")
        return audio_path

    @staticmethod
    async def _synthesize(text: str, output_path: Path) -> None:
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(str(output_path))
