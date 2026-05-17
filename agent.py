#!/usr/bin/env python3
"""
AI Video Generator — Orchestrator
-----------------------------------
Delegates each step to a dedicated sub-agent:

  1. NewsFetcherAgent   — scrapes RSS feeds for latest AI news
  2. ScriptWriterAgent  — uses Claude to write a structured scene script
  3. VoiceoverAgent     — synthesizes TTS (or accepts a provided audio file)
  4. VideoAssemblerAgent — generates DALL-E images and assembles the final MP4

Usage:
  python agent.py                        # full auto mode
  python agent.py --audio path/to/vo.mp3 # skip TTS, use your own audio
  python agent.py --output-dir ./videos  # custom output directory
"""

import argparse
import sys
import time
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

from agents.news_fetcher import NewsFetcherAgent
from agents.script_writer import ScriptWriterAgent
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir) / date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  AI Video Generator — YouTube AI News Channel")
    print("=" * 60)
    t0 = time.time()

    # ── Sub-agent 1: Fetch news ────────────────────────────────────
    news_agent = NewsFetcherAgent()
    stories = news_agent.run()
    if not stories:
        print("[Orchestrator] No stories found. Aborting.")
        sys.exit(1)

    # ── Sub-agent 2: Write script ──────────────────────────────────
    script_agent = ScriptWriterAgent()
    script = script_agent.run(stories)

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

    elapsed = time.time() - t0
    print()
    print("=" * 60)
    print(f"  Done in {elapsed:.0f}s")
    print(f"  Video  → {video_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
