"""
Sub-agent: Generates a YouTube thumbnail from the script's thumbnail_concept.
Uses Google Imagen 3 with native 16:9 aspect ratio, then resizes to the
standard YouTube thumbnail size of 1280x720.
Output: output_dir/thumbnail.png
"""

import os
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image

IMAGEN_MODEL = "imagen-3.0-generate-002"
THUMBNAIL_SIZE = (1280, 720)


class ThumbnailAgent:
    """Generates a ready-to-upload YouTube thumbnail via Google Imagen 3."""

    def __init__(self) -> None:
        self.client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

    def run(self, script: dict, output_dir: Path) -> Path:
        out_path = output_dir / "thumbnail.png"
        if out_path.exists():
            print(f"[Thumbnail] Reusing existing thumbnail → {out_path}")
            return out_path

        concept = script.get("thumbnail_concept", "")
        if not concept:
            raise ValueError("Script is missing 'thumbnail_concept'")

        prompt = (
            f"{concept} "
            "YouTube thumbnail style, bold and eye-catching, "
            "photorealistic or digital art, high contrast, vibrant colors, "
            "no text overlays."
        )

        print("[Thumbnail] Generating thumbnail with Google Imagen 3...")
        response = self.client.models.generate_images(
            model=IMAGEN_MODEL,
            prompt=prompt[:1000],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            ),
        )
        img_bytes = response.generated_images[0].image.image_bytes
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img = img.resize(THUMBNAIL_SIZE, Image.LANCZOS)
        img.save(str(out_path), "PNG")

        print(f"[Thumbnail] Saved → {out_path}")
        return out_path
