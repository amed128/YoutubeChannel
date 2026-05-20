#!/usr/bin/env python3
"""
AI Video Generator — Orchestrator
-----------------------------------
Delegates each step to a dedicated sub-agent:

  1. NewsFetcherAgent    — scrapes RSS feeds for latest AI news
  2. ScriptWriterAgent   — uses Claude to write a structured scene script
  3. VoiceoverAgent      — synthesizes TTS (or accepts a provided audio file)
  4. VideoAssemblerAgent — generates DALL-E images and assembles the final MP4
  5. ThumbnailAgent      — generates a YouTube thumbnail via DALL-E 3

Usage:
  python agent.py                               # full auto mode
  python agent.py --dry-run                     # script preview only (no TTS/DALL-E)
  python agent.py --script path/to/script.json  # skip news + Claude, use pre-built script
  python agent.py --audio path/to/vo.mp3        # skip TTS, use your own audio
  python agent.py --output-dir ./videos         # custom output directory
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from agents.news_fetcher import NewsFetcherAgent
from agents.script_writer import ScriptWriterAgent
from agents.thumbnail import ThumbnailAgent
from agents.video_assembler import VideoAssemblerAgent
from agents.voiceover import VoiceoverAgent

load_dotenv()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI YouTube news video generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--audio",
        metavar="PATH",
        help="Path to a pre-recorded voiceover file (MP3/WAV). "
             "If omitted, OpenAI TTS is used.",
    )
    parser.add_argument(
        "--output-dir",
        metavar="DIR",
        default="output",
        help="Directory where the final MP4 is saved. Default: ./output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stop after script generation: print titles + scene breakdown, skip TTS and DALL-E.",
    )
    parser.add_argument(
        "--script",
        metavar="PATH",
        help="Path to a pre-generated script JSON file. Skips news fetching and Claude script writing.",
    )
    return parser.parse_args()


def _print_dry_run_preview(script: dict) -> None:
    print()
    print("=" * 60)
    print("  DRY-RUN — Script Preview (no TTS / DALL-E charged)")
    print("=" * 60)
    print("\nViral Titles:")
    for i, t in enumerate(script.get("viral_titles", []), 1):
        print(f"  {i}. {t}")
    print(f"\nThumbnail concept:\n  {script.get('thumbnail_concept', 'N/A')}")
    print(f"\nScenes ({len(script.get('scenes', []))}):")
    for scene in script.get("scenes", []):
        n = scene["scene_number"]
        dur = scene["duration_seconds"]
        narration_preview = scene["narration"][:80].replace("\n", " ")
        if len(scene["narration"]) > 80:
            narration_preview += "…"
        print(f"  [{n:02d}] {dur}s  {narration_preview}")
    total = sum(s["duration_seconds"] for s in script.get("scenes", []))
    print(f"\n  Total estimated duration: {total}s ({total // 60}m {total % 60}s)")
    print()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir) / date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  AI Video Generator — YouTube AI News Channel")
    print("=" * 60)
    t0 = time.time()

    if args.script:
        script_path = Path(args.script)
        if not script_path.exists():
            print(f"[Orchestrator] Script file not found: {script_path}")
            sys.exit(1)
        script = json.loads(script_path.read_text())
        print(f"[Orchestrator] Loaded pre-generated script from {script_path}")
    else:
        # ── Sub-agent 1: Fetch news ────────────────────────────────────
        news_agent = NewsFetcherAgent()
        stories = news_agent.run()
        if not stories:
            print("[Orchestrator] No stories found. Aborting.")
            sys.exit(1)

        # ── Sub-agent 2: Write script ──────────────────────────────────
        script_agent = ScriptWriterAgent()
        script = script_agent.run(stories)

    if args.dry_run:
        _print_dry_run_preview(script)
        sys.exit(0)

    # ── Sub-agent 3: Voiceover ─────────────────────────────────────
    voice_agent = VoiceoverAgent()
    audio_path = voice_agent.run(
        script=script,
        output_dir=output_dir,
        provided_audio=args.audio,
    )

    # ── Sub-agent 4: Assemble video ────────────────────────────────
    assembler = VideoAssemblerAgent()
    video_path = assembler.run(
        script=script,
        audio_path=audio_path,
        output_dir=output_dir,
    )

    # ── Sub-agent 5: Thumbnail ─────────────────────────────────────
    thumb_agent = ThumbnailAgent()
    thumb_path = thumb_agent.run(script=script, output_dir=output_dir)

    elapsed = time.time() - t0
    print()
    print("=" * 60)
    print(f"  Done in {elapsed:.0f}s")
    print(f"  Video     → {video_path}")
    print(f"  Thumbnail → {thumb_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
