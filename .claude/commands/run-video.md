You are running the AI YouTube video pipeline for a Spanish-language faceless channel targeting Hispanic entrepreneurs.

## Your job (3 steps)

### Step 1 — Find the latest AI news

Use WebSearch to find AI news from the last 48 hours. Run these searches:
- "artificial intelligence news today 2026"
- "AI tools for business 2026"
- "ChatGPT OpenAI news this week"
- "Claude Gemini AI announcements"

Pick the **5–8 most relevant stories** for Hispanic entrepreneurs (practical, actionable, business-focused). For each story collect: title, 2–3 sentence summary, source.

### Step 2 — Write the Spanish video script

Using the stories you found, generate a structured JSON script following these rules:

**Audience:** Hispanic entrepreneurs from Spain, Mexico, Colombia (25–45 years old). Not technical — they want practical results they can apply today.

**5 Writing rules:**
1. **Explosive hook in the first 5 seconds** — open with a shocking stat, provocative question, or unexpected claim. NEVER start with "Hola a todos" or "Bienvenidos".
2. **Neutral, dynamic Spanish** — use "tú", short sentences, fast rhythm, zero filler. Explain technical concepts with simple analogies.
3. **Open loops** — mid-script, promise to reveal something valuable before the end to retain viewers.
4. **Visual instructions in English** — after each narration block, picture a faceless YouTube scene (screen recording, animated graphic, B-roll, dynamic zoom, etc.)
5. **Natural CTA** — end with a genuine subscription call-to-action, not robotic. If tools are mentioned, add affiliate hook phrases: "link en la descripción", "pruébalo gratis desde el link de abajo".

**Output JSON schema (strict — no markdown, no extra text):**
```json
{
  "viral_titles": [
    "<Viral title 1, max 70 chars, SEO + CTR optimized>",
    "<Viral title 2>",
    "<Viral title 3>"
  ],
  "thumbnail_concept": "<2-4 sentences describing the ideal thumbnail: colors, expression, text overlay, style, high CTR>",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "<Spanish text the narrator reads aloud>",
      "visual_prompt": "<English description for DALL-E background image: photorealistic, cinematic, no text overlays>",
      "duration_seconds": 10
    }
  ]
}
```

**Schema rules:**
- `viral_titles`: exactly 3 titles — emotional, with a number or concrete promise
- `thumbnail_concept`: describes the ideal thumbnail visually
- `scenes`: 6–10 scenes. Scene 1 = hook. Last scene = CTA.
- `narration`: real Spanish text read aloud
- `visual_prompt`: English description for DALL-E 3 (no text in the image)
- `duration_seconds`: integer between 6 and 25

### Step 3 — Save and run the pipeline

1. Determine today's output directory: `output/YYYY-MM-DD/` (use today's actual date)
2. Create it if needed: use Bash `mkdir -p output/YYYY-MM-DD`
3. Save the JSON script to `output/YYYY-MM-DD/script.json` using the Write tool
4. Run the Python pipeline:
   ```bash
   python3 agent.py --script output/YYYY-MM-DD/script.json
   ```
5. Report the output paths (video + thumbnail) when done.

## Notes
- If `pip` dependencies aren't installed yet, run `pip3 install -r requirements.txt` first.
- If the pipeline fails mid-way, re-running with the same `--script` flag is safe — Imagen 3 images and thumbnail that already exist are reused automatically.
- The `GOOGLE_API_KEY` must be set in the `.env` file before running. Get a free key at https://aistudio.google.com/apikey
- TTS is handled by `edge-tts` (free, no API key needed).
