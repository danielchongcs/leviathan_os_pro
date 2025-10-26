"""Reddit ingestor: fetch latest posts from selected subreddits."""

from __future__ import annotations

import os
from typing import Any

import praw

CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "leviathan-bot/0.1")

SUBS: tuple[str, ...] = ("singapore", "RealEstate", "PropertyInvestment")
LIMIT: int = 25


def _client() -> praw.Reddit | None:
    """Create praw client if creds exist; otherwise return None."""
    if not (CLIENT_ID and CLIENT_SECRET and USER_AGENT):
        return None
    return praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
        check_for_async=False,
    )


def search(_: Any) -> list[dict[str, str | None]]:
    """Return latest posts from the configured subreddits."""
    reddit = _client()
    if reddit is None:
        return []

    out: list[dict[str, str | None]] = []
    try:
        for sub in SUBS:
            for it in reddit.subreddit(sub).new(limit=LIMIT):
                out.append(
                    {
                        "title": it.title,
                        "subreddit": it.subreddit.display_name,
                        "created_utc": str(int(it.created_utc)),
                        "id": it.id,
                        "url": it.url,
                    }
                )
    except Exception:  # pylint: disable=broad-exception-caught
        # PRAW can raise several runtime errors (e.g., rate limits or network issues)
        return []
    return out
