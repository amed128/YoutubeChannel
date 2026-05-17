# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repo contains Python scripting experiments plus the main project: **`ai_video_agent/`** — a multi-agent CLI pipeline that automatically produces YouTube AI-news videos in Spanish.

## ai_video_agent — Running & Setup

```bash
# Install dependencies (from ai_video_agent/)
pip install -r ai_video_agent/requirements.txt

# Copy and fill in API keys
cp ai_video_agent/.env.example ai_video_agent/.env

# Run the full pipeline
python ai_video_agent/agent.py

# Skip TTS and use your own audio file
python ai_video_agent/agent.py --audio path/to/voiceover.mp3

# Change output directory (default: output/YYYY-MM-DD/)
python ai_video_agent/agent.py --output-dir ./videos
```

There is no test suite or linter configured yet.

## ai_video_agent — Architecture

The orchestrator (`agent.py`) runs four sub-agents in strict sequence; each is a class with a single `run()` method in `agents/`:

```
NewsFetcherAgent → ScriptWriterAgent → VoiceoverAgent → VideoAssemblerAgent
     RSS feeds        Claude Opus 4.7     OpenAI TTS        DALL-E 3 + MoviePy
```

**Data flow between agents:**

| Step | Input | Output |
|---|---|---|
| `NewsFetcherAgent.run()` | — | `list[dict]` with `title, summary, url, source, published` |
| `ScriptWriterAgent.run(stories)` | stories list | `script` dict (see schema below) |
| `VoiceoverAgent.run(script, output_dir, provided_audio)` | script + optional audio path | `Path` to `.mp3` |
| `VideoAssemblerAgent.run(script, audio_path, output_dir)` | script + audio path | `Path` to final `.mp4` |

**Script dict schema** (produced by `ScriptWriterAgent`, consumed by the other two):
```json
{
  "viral_titles": ["<title 1>", "<title 2>", "<title 3>"],
  "thumbnail_concept": "<description for thumbnail design>",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "<Spanish text read aloud>",
      "visual_prompt": "<English DALL-E prompt for background image>",
      "duration_seconds": 10
    }
  ]
}
```

**Key implementation details:**
- `ScriptWriterAgent` uses Claude Opus 4.7 with `thinking: {"type": "adaptive"}` and prompt caching (`cache_control: ephemeral`) on the system prompt. The system prompt enforces Spanish-language output for Hispanic entrepreneurs with 5 writing rules (explosive hook, neutral Spanish, open loops, English `[SCENE:]` visual cues, natural CTA).
- `VideoAssemblerAgent` skips DALL-E re-generation if `scene_NN.png` already exists in `output_dir` — safe to re-run after a partial failure.
- `VoiceoverAgent` concatenates all scene narrations into one TTS call (cheaper than per-scene calls).
- Output files land in `output/YYYY-MM-DD/`: `scene_NN.png` images, `voiceover.mp3`, and the final `<title>.mp4`.
- `output/` is gitignored.

## Environment Variables

Both keys are required; set them in `ai_video_agent/.env`:
- `ANTHROPIC_API_KEY` — Claude API (script generation)
- `OPENAI_API_KEY` — DALL-E 3 images + TTS voiceover

## Other Scripts in This Repo

These are standalone experiments, not part of the video pipeline:
- `youtube_api/` — `Yt_stats` class wrapping YouTube Data API v3 (channel stats, video list)
- `bsp_scraping/` — BeautifulSoup scraping experiments
- `py_selenium/` — Selenium automation scripts
- `requests_module/` — Basic `requests` usage examples
- `webbrowser/` — `webbrowser` module usage
