"""
Sub-agent: Builds the final MP4.
Steps:
  1. Generate one background image per scene using DALL-E 3.
  2. Create a video clip for each scene (image + duration).
  3. Add subtitle text overlay (scene narration).
  4. Concatenate all clips.
  5. Mix in the voiceover audio track.
  6. Export final MP4 to output_dir.
"""

import os
import textwrap
from pathlib import Path

import openai
import requests
from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    concatenate_videoclips,
)
from PIL import Image

VIDEO_SIZE = (1920, 1080)   # 1080p landscape
FONT_SIZE = 42
FONT_COLOR = "white"
FONT = "DejaVu-Sans-Bold"
SUBTITLE_WRAP = 70          # chars per subtitle line
DALLE_MODEL = "dall-e-3"
DALLE_SIZE = "1792x1024"    # closest DALL-E 3 size to 16:9


class VideoAssemblerAgent:
    """Generates images and assembles the final MP4."""

    def __init__(self) -> None:
        self.client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def run(self, script: dict, audio_path: Path, output_dir: Path) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        clips = []

        for scene in script["scenes"]:
            n = scene["scene_number"]
            print(f"[VideoAssembler] Scene {n}/{len(script['scenes'])} — generating image...")
            img_path = self._generate_image(scene, output_dir, n)
            clip = self._make_scene_clip(scene, img_path)
            clips.append(clip)

        print("[VideoAssembler] Concatenating scenes...")
        video = concatenate_videoclips(clips, method="compose")

        print("[VideoAssembler] Mixing audio...")
        audio = AudioFileClip(str(audio_path))
        # Trim audio to video length (or pad if shorter)
        if audio.duration > video.duration:
            audio = audio.subclipped(0, video.duration)
        video = video.with_audio(audio)

        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in script["title"])
        out_path = output_dir / f"{safe_title[:60]}.mp4"
        print(f"[VideoAssembler] Rendering → {out_path}")
        video.write_videofile(
            str(out_path),
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None,
        )
        return out_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_image(self, scene: dict, output_dir: Path, idx: int) -> Path:
        img_path = output_dir / f"scene_{idx:02d}.png"
        if img_path.exists():
            return img_path  # reuse if already generated (re-run safety)

        prompt = (
            f"{scene['visual_prompt']} "
            "Photorealistic, cinematic lighting, 16:9 aspect ratio, "
            "high quality, no text overlays."
        )
        response = self.client.images.generate(
            model=DALLE_MODEL,
            prompt=prompt[:1000],
            size=DALLE_SIZE,
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        img_bytes = requests.get(image_url, timeout=30).content  # type: ignore[arg-type]

        # Convert to exact VIDEO_SIZE PNG
        from io import BytesIO
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = img.resize(VIDEO_SIZE, Image.LANCZOS)
        img.save(str(img_path), "PNG")
        return img_path

    def _make_scene_clip(self, scene: dict, img_path: Path) -> CompositeVideoClip:
        duration = int(scene["duration_seconds"])
        base = ImageClip(str(img_path)).with_duration(duration)

        # Subtitle text
        wrapped = "\n".join(textwrap.wrap(scene["narration"], width=SUBTITLE_WRAP))
        subtitle = (
            TextClip(
                text=wrapped,
                font=FONT,
                font_size=FONT_SIZE,
                color=FONT_COLOR,
                stroke_color="black",
                stroke_width=2,
                method="caption",
                size=(VIDEO_SIZE[0] - 160, None),
            )
            .with_duration(duration)
            .with_position(("center", VIDEO_SIZE[1] - 200))
        )

        return CompositeVideoClip([base, subtitle], size=VIDEO_SIZE)
