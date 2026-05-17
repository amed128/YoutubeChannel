"""
Sub-agent: Fetches the latest AI news from RSS feeds.
Returns a list of story dicts: {title, summary, url, source}.
"""

import feedparser
import re
from datetime import datetime, timezone
from typing import Any

RSS_FEEDS = [
    ("HuggingFace Blog", "https://huggingface.co/blog/feed.xml"),
    ("Google AI Blog", "https://blog.google/technology/ai/rss/"),
    ("MIT News – AI", "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"),
    ("VentureBeat AI", "https://feeds.feedburner.com/venturebeat/SZYF"),
    ("The Decoder", "https://the-decoder.com/feed/"),
]

MAX_STORIES = 10


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def _parse_published(entry: Any) -> datetime:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.min.replace(tzinfo=timezone.utc)


class NewsFetcherAgent:
    """Scrapes RSS feeds and returns deduplicated, sorted AI news stories."""

    def run(self) -> list[dict]:
        print("[NewsFetcher] Fetching AI news from RSS feeds...")
        stories: list[dict] = []
        seen_titles: set[str] = set()

        for source_name, url in RSS_FEEDS:
            try:
                feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
                for entry in feed.entries[:5]:
                    title = _strip_html(entry.get("title", "")).strip()
                    if not title or title.lower() in seen_titles:
                        continue
                    seen_titles.add(title.lower())
                    summary = _strip_html(entry.get("summary", entry.get("description", "")))
                    summary = summary[:600]  # cap length
                    stories.append(
                        {
                            "title": title,
                            "summary": summary,
                            "url": entry.get("link", ""),
                            "source": source_name,
                            "published": _parse_published(entry),
                        }
                    )
            except Exception as exc:
                print(f"[NewsFetcher] Warning: could not parse {source_name}: {exc}")

        # Sort newest-first, take top N
        stories.sort(key=lambda s: s["published"], reverse=True)
        stories = stories[:MAX_STORIES]

        print(f"[NewsFetcher] Found {len(stories)} stories.")
        return stories
