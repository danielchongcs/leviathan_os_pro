"""YouTube search ingestor."""

from __future__ import annotations

import os
from typing import Any, Dict

import requests

API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
QUERY: str = "singapore real estate"
MAX_RESULTS: int = 25


def search(_: Any) -> list[dict[str, str | None]]:
    """Return the latest YouTube videos for QUERY."""
    if not API_KEY:
        return []

    url = "https://www.googleapis.com/youtube/v3/search"
    # Use a precise union so mypy accepts requests.get(..., params=...)
    params: Dict[str, str | int] = {
        "key": API_KEY,
        "part": "snippet",
        "q": QUERY,
        "maxResults": MAX_RESULTS,  # int is fine here
        "type": "video",
        "order": "date",
    }

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError):
        return []

    out: list[dict[str, str | None]] = []
    for it in data.get("items", []):
        s = it.get("snippet", {})
        out.append(
            {
                "title": s.get("title"),
                "channel": s.get("channelTitle"),
                "published_at": s.get("publishedAt"),
                "video_id": it.get("id", {}).get("videoId"),
            }
        )
    return out
