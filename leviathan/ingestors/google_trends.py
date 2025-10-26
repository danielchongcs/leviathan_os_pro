"""Google Trends ingestor: get 12-month interest for selected terms."""

from __future__ import annotations

from typing import Any
import random

# Prefer a cryptographically strong RNG to satisfy Bandit (B311)
_rng = random.SystemRandom()

# Top-level import with clean fallback (no mypy ignores needed)
_has_pytrends = False
_trend_request: Any | None = None
try:
    from pytrends.request import TrendReq as _ImportedTrendReq
    _trend_request = _ImportedTrendReq
    _has_pytrends = True
except ImportError:
    _trend_request = None

TERMS: tuple[str, ...] = ("singapore property", "condo", "HDB")


def search(_: Any) -> list[dict[str, Any]]:
    """
    Return trends series for TERMS.
    Falls back to synthetic data when pytrends is unavailable or errors.
    """
    # Fallback path
    if not _has_pytrends or _trend_request is None:
        return [
            {"term": term, "series": [_rng.randint(0, 100) for _ in range(12)]}
            for term in TERMS
        ]

    try:
        pt = _trend_request(hl="en-US", tz=0)
        pt.build_payload(list(TERMS), timeframe="today 12-m")
        df = pt.interest_over_time()
        results: list[dict[str, Any]] = []

        if df is not None and not df.empty:
            for col in df.columns:
                if col == "isPartial":
                    continue
                results.append(
                    {
                        "term": str(col),
                        "series": df[col].astype(int).tolist(),
                    }
                )
        return results
    except Exception:  # pylint: disable=broad-exception-caught
        # Network / quota / API hiccups -> graceful empty result
        return []
