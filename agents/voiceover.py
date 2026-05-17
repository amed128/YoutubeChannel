"""
Sub-agent: Generates voiceover audio from the script narration.
Priority:
  1. User-provided audio file path (--audio flag) — used as-is.
  2. OpenAI TTS API — synthesizes speech scene by scene, then concatenates.
"""

import os
import struct
import wave
from pathlib import Path

import openai


VOICE = "onyx"          # Options: alloy, echo, fable, onyx, nova, shimmer
TTS_MODEL = "tts-1-hd"


def _concatenate_wav_bytes(wav_chunks: list[bytes]) -> bytes:
    """Merge multiple WAV byte blobs into a single WAV blob."""
    frames_list: list[bytes] = []
    params: tuple | None = None

    for chunk in wav_chunks:
        with wave.open(__import__("io").BytesIO(chunk)) as wf:
            if params is None:
                params = wf.getparams()
            frames_list.append(wf.readframes(wf.getnframes()))

    buf = __import__("io").BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setparams(params)  # type: ignore[arg-type]
        for frames in frames_list:
            wf.writeframes(frames)
    return buf.getvalue()


class VoiceoverAgent:
    """Generates or passes through the audio track for the video."""

    def __init__(self) -> None:
        self.client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

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

        print("[Voiceover] Synthesizing speech with OpenAI TTS...")
        output_dir.mkdir(parents=True, exist_ok=True)
        full_narration = " ".join(s["narration"] for s in script["scenes"])
        audio_path = output_dir / "voiceover.mp3"

        # Single API call — concatenated narration is simpler and cheaper
        response = self.client.audio.speech.create(
            model=TTS_MODEL,
            voice=VOICE,
            input=full_narration,
            response_format="mp3",
        )
        audio_path.write_bytes(response.content)
        print(f"[Voiceover] Audio saved → {audio_path}")
        return audio_path
