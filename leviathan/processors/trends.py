"""Lightweight trend helpers (pure-python, typed, linter-friendly)."""
from __future__ import annotations

from typing import Any, Iterable, List, Sequence


def _as_floats(series: Iterable[float | int]) -> List[float]:
    """Convert incoming sequence to list of floats."""
    return [float(x) for x in series]


def minmax_normalize(series: Sequence[float | int]) -> List[float]:
    """Scale to [0, 1]. Returns zeros if constant/empty."""
    vals = _as_floats(series)
    if not vals:
        return []
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        return [0.0 for _ in vals]
    return [(v - lo) / (hi - lo) for v in vals]


def pct_change(series: Sequence[float | int]) -> List[float]:
    """Percent change between consecutive points."""
    vals = _as_floats(series)
    out: List[float] = []
    for i in range(1, len(vals)):
        prev = vals[i - 1]
        out.append(0.0 if prev == 0 else (vals[i] - prev) / prev)
    return out


def simple_slope(series: Sequence[float | int]) -> float:
    """Very small O(n) slope proxy (last-first over n)."""
    vals = _as_floats(series)
    if len(vals) < 2:
        return 0.0
    return (vals[-1] - vals[0]) / (len(vals) - 1)


def label_trend(series: Sequence[float | int], flat_eps: float = 0.02) -> str:
    """
    Label up/down/flat using slope and last 3-step change.
    flat_eps is the absolute threshold for 'flat'.
    """
    vals = _as_floats(series)
    if len(vals) < 2:
        return "flat"
    slope = simple_slope(vals)
    last_delta = vals[-1] - vals[max(0, len(vals) - 4)]
    score = slope + (last_delta / (abs(vals[-2]) + 1e-9))

    if score > flat_eps:
        return "up"
    if score < -flat_eps:
        return "down"
    return "flat"


def keep_unknown_terms(terms: Sequence[str], known: set[str]) -> List[str]:
    """Return terms not already in the known set (no globals!)."""
    return [t for t in terms if t not in known]


# Optional no-op API to match previous callsites that passed an unused arg.
def summarize(_: Any = None) -> dict[str, Any]:
    """Stub processor entrypoint that returns empty summary."""
    return {}
