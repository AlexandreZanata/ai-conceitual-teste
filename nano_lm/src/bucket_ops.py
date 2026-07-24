"""H-BUCKET: length-banded BAT; pad only within band; tok/s gate vs H-BAT."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "DEFAULT_BAND",
    "assign_length_buckets",
    "decide_hbucket",
]

DEFAULT_BAND = 4


def assign_length_buckets(
    lengths: list[int], *, band: int = DEFAULT_BAND
) -> list[list[int]]:
    """
    GIVEN prompt token lengths and a band width
    WHEN grouping indices
    THEN return non-empty buckets sorted by band key (stable within bucket).
    """
    if int(band) < 1:
        raise ValueError("band must be >= 1")
    if not lengths:
        raise ValueError("assign_length_buckets: empty lengths")
    bags: dict[int, list[int]] = {}
    for i, n in enumerate(lengths):
        key = (int(n) - 1) // int(band)
        bags.setdefault(key, []).append(i)
    return [bags[k] for k in sorted(bags)]


def decide_hbucket(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-BUCKET vs H-BAT (+ optional serial H-EARLY)
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε vs BAT (and EARLY if present) and tok/s > BAT.
    """
    bat = stats.get("H-BAT")
    if bat is None:
        return "needs H-BAT control"
    if abs(float(s["mean_lp"]) - float(bat["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-BAT)"
    early = stats.get("H-EARLY")
    if early is not None:
        if abs(float(s["mean_lp"]) - float(early["mean_lp"])) > float(eps_lp):
            return "KILL (lp change vs serial EARLY)"
    if float(s["mean_tps"]) <= float(bat["mean_tps"]):
        return "KILL (no tok/s win vs H-BAT)"
    return "PROMOTE (length-bucketed throughput vs H-BAT)"
