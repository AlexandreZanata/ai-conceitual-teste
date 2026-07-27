"""Wave AQ3 H-LATP: latency p50/p99 for LOOKUP · PEAK · DECODE."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aq_session_ops import AQ0_LATENCY_PATHS, AQ0_LATENCY_PROTOCOL, map_product_mode

__all__ = [
    "LATP_ID",
    "LATP_THESIS",
    "LATP_PATHS",
    "FASTBASE_HOT_WALL_MS",
    "LOOKUP_N",
    "PEAK_N",
    "DECODE_N",
    "percentile",
    "path_latency_stats",
    "telemetry_rules_ok",
    "peak_regressed",
    "decide_latp",
]

LATP_ID = "H-LATP"
LATP_PATHS = AQ0_LATENCY_PATHS
# Published AP4 FASTBASE hot wall (formal-hfastbase-fastbase.md / summary).
FASTBASE_HOT_WALL_MS = 0.0471135997941019
LOOKUP_N = 64
PEAK_N = 256
DECODE_N = 12
LATP_THESIS = (
    "Publish p50/p99 wall_ms for LOOKUP · PEAK · DECODE; "
    "no silent regress vs FASTBASE hot; LOOKUP wall=0 ≠ speed IQ"
)


def percentile(values: Sequence[float], p: float) -> float:
    """
    GIVEN sorted-or-unsorted wall samples and p in [0,100]
    WHEN computing percentile
    THEN return linear-interpolated percentile (empty → 0.0).
    """
    if not values:
        return 0.0
    if p <= 0:
        return float(min(values))
    if p >= 100:
        return float(max(values))
    xs = sorted(float(v) for v in values)
    n = len(xs)
    if n == 1:
        return xs[0]
    rank = (p / 100.0) * (n - 1)
    lo = int(rank)
    hi = min(lo + 1, n - 1)
    frac = rank - lo
    return float(xs[lo] * (1.0 - frac) + xs[hi] * frac)


def path_latency_stats(walls: Sequence[float]) -> dict[str, float | int]:
    """
    GIVEN wall_ms samples for one path
    WHEN summarizing
    THEN p50 · p99 · mean · n.
    """
    xs = [float(v) for v in walls]
    n = len(xs)
    mean = float(sum(xs) / n) if n else 0.0
    return {
        "n": n,
        "mean_wall_ms": mean,
        "p50_wall_ms": percentile(xs, 50),
        "p99_wall_ms": percentile(xs, 99),
    }


def telemetry_rules_ok(
    *,
    path: str,
    walls: Sequence[float],
    n_news: Sequence[int],
    modes: Sequence[str],
) -> bool:
    """
    GIVEN AQ0 latency protocol rules
    WHEN checking a path sample set
    THEN True iff LOOKUP may be 0; PEAK/DECODE require wall>0; DECODE n_new>0.
    """
    if path not in LATP_PATHS or not walls:
        return False
    if path == "LOOKUP":
        return all(map_product_mode(m) == "LOOKUP" for m in modes)
    if path == "PEAK":
        if not all(float(w) > 0.0 for w in walls):
            return False
        return all(
            map_product_mode(m) == "PEAK" or "PEAK" in str(m).upper()
            for m in modes
        )
    if len(n_news) != len(walls):
        return False
    if not all(float(w) > 0.0 and int(n) > 0 for w, n in zip(walls, n_news)):
        return False
    return all(map_product_mode(m) == "DECODE" for m in modes)


def peak_regressed(peak_p50: float, *, baseline: float = FASTBASE_HOT_WALL_MS) -> bool:
    """True iff PEAK p50 is slower than published FASTBASE hot."""
    return float(peak_p50) > float(baseline)


def decide_latp(
    *,
    paths: Mapping[str, Mapping[str, Any]],
    telemetry_ok: Mapping[str, bool],
    regress_noted: bool,
) -> str:
    """
    GIVEN published path stats + telemetry flags + regress note
    WHEN applying pesquisa §5 AQ3 gate
    THEN KILL if missing/broken; KILL if regress without note; else PROMOTE.
    """
    for path in LATP_PATHS:
        if path not in paths:
            return "KILL"
        st = paths[path]
        if "p50_wall_ms" not in st or "p99_wall_ms" not in st:
            return "KILL"
        if not bool(telemetry_ok.get(path)):
            return f"KILL (telemetry broken: {path})"
    peak_p50 = float(paths["PEAK"]["p50_wall_ms"])
    if peak_regressed(peak_p50) and not regress_noted:
        return "KILL (PEAK regress vs FASTBASE hot without note)"
    _ = AQ0_LATENCY_PROTOCOL  # charter frozen in AQ0
    return "PROMOTE"
