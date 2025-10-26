"""General utility helpers for Leviathan."""

import json
import math
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd


def safe_read_json(path: str, default: Any = None) -> Dict[str, Any]:
    """Safely read a JSON file and return its contents as a dictionary.

    Args:
        path: Path to the JSON file.
        default: Value to return if file does not exist or cannot be read.

    Returns:
        A dictionary with the JSON content or the default value.
    """
    p = Path(path)
    if not p.exists():
        return {} if default is None else default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON decode error in {path}: {e}")
        return {} if default is None else default
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"⚠️ Unexpected error reading {path}: {e}")
        return {} if default is None else default


def normalize(x: float) -> float:
    """Normalize a numeric value to the range [0, 1] using a logarithmic scale."""
    return math.log1p(max(x, 0)) / math.log(1 + 1000)


def score(count: float, velocity: float, novelty: float) -> float:
    """Compute a weighted trend score based on count, velocity, and novelty."""
    return (0.4 * normalize(count) + 0.8 * velocity + 0.8 * novelty) / 2.0


def to_df(signals: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert a list of signal dictionaries into a sorted pandas DataFrame."""
    rows = []
    for s in signals:
        rows.append(
            {
                "phrase": s.get("phrase"),
                "domain": s.get("domain", ""),
                "count": s.get("count", 0),
                "velocity": round(s.get("velocity", 0), 3),
                "novelty": round(s.get("novelty", 0), 3),
                "score": round(
                    score(
                        s.get("count", 0),
                        s.get("velocity", 0),
                        s.get("novelty", 0),
                    ),
                    3,
                ),
                "examples": ", ".join(s.get("examples", [])[:3]),
            }
        )
    return pd.DataFrame(rows).sort_values("score", ascending=False).reset_index(drop=True)


def hooks(phrase: str) -> Dict[str, str]:
    """Generate ad-style hooks and short headlines for a given keyword phrase."""
    return {
        "ad": f"{phrase.title()} — Fix It In 24 Hours",
        "short": f"{phrase.title()}: The 30-Second Fix No One Told You",
        "h1": f"{phrase.title()} • Finally, A Simple Solution",
    }


def expand_keywords(seed: str) -> List[str]:
    """Expand a single keyword into a list of search phrases for trend discovery."""
    seed = seed.strip().lower()
    patterns = [
        f"{seed} singapore",
        f"best {seed}",
        f"{seed} near me",
        f"{seed} price",
        f"how to {seed}",
        f"{seed} for smes",
        f"{seed} for students",
        f"{seed} b2b",
        f"{seed} ai",
        f"{seed} automation",
    ]
    return list(dict.fromkeys(patterns))
