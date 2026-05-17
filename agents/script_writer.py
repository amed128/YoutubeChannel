"""
Sub-agent: Uses Claude to turn raw news stories into a structured video script.
Output is a validated Python dict matching the VideoScript schema.
"""

import json
import os
from datetime import date

import anthropic

SYSTEM_PROMPT = """\
You are a professional scriptwriter for a YouTube channel dedicated to AI news.
Your job is to turn raw news stories into an engaging, short-form video script.

Guidelines:
- Write in a clear, informative, and slightly conversational tone.
- Each scene has one key idea and a matching visual description.
- Keep total narration under 3 minutes when read at normal speed (~150 wpm).
- The intro scene must hook the viewer in the first 10 seconds.
- The outro scene wraps up with a call-to-action ("Like & Subscribe").
- Respond ONLY with valid JSON — no markdown fences, no extra prose.

JSON schema:
{
  "title": "<video title, max 80 chars>",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "<text to be read aloud for this scene>",
      "visual_prompt": "<DALL-E prompt for the background image>",
      "duration_seconds": <integer 6..20>
    }
  ]
}
"""


class ScriptWriterAgent:
    """Calls Claude to generate a structured scene-by-scene script."""

    def __init__(self) -> None:
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def run(self, stories: list[dict]) -> dict:
        print("[ScriptWriter] Generating script with Claude...")
        today = date.today().strftime("%B %d, %Y")
        stories_text = "\n\n".join(
            f"## {i+1}. {s['title']} ({s['source']})\n{s['summary']}"
            for i, s in enumerate(stories)
        )
        user_message = (
            f"Today is {today}.\n\n"
            f"Here are the latest AI news stories:\n\n{stories_text}\n\n"
            "Write a 5–8 scene video script covering the most important stories."
        )

        response = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_message}],
        )

        raw = next(b.text for b in response.content if b.type == "text")
        script = json.loads(raw)
        self._validate(script)
        print(f"[ScriptWriter] Script ready: '{script['title']}' — {len(script['scenes'])} scenes.")
        return script

    @staticmethod
    def _validate(script: dict) -> None:
        assert "title" in script, "Missing 'title'"
        assert "scenes" in script and script["scenes"], "Missing 'scenes'"
        for s in script["scenes"]:
            for key in ("scene_number", "narration", "visual_prompt", "duration_seconds"):
                assert key in s, f"Scene missing '{key}'"
