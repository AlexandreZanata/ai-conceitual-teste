"""Wave AS5 H-METRICS: latency p50/p99 tetrad(+ABSTAIN) + KB coverage refresh."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from as_session_ops import (
    AS0_LATENCY_PATHS,
    AS0_METRICS_PROTOCOL,
    AS0_MODES,
    map_as_product_mode,
)
from kbcov_ops import PRODUCT_HOLES
from latp_ops import (
    FASTBASE_HOT_WALL_MS,
    path_latency_stats,
    peak_regressed,
    percentile,
)

__all__ = [
    "METRICS_ID",
    "METRICS_THESIS",
    "METRICS_PATHS",
    "METRICS_PROTOCOL",
    "FASTBASE_HOT_WALL_MS",
    "LOOKUP_N",
    "PEAK_N",
    "DECODE_N",
    "ABSTAIN_N",
    "PRODUCT_HOLES",
    "percentile",
    "path_latency_stats",
    "peak_regressed",
    "map_as_product_mode",
    "telemetry_rules_ok",
    "protocol_ok",
    "kb_gate_ok",
    "decide_metrics",
]

METRICS_ID = "H-METRICS"
METRICS_PATHS = AS0_LATENCY_PATHS  # LOOKUP · PEAK · DECODE · ABSTAIN
METRICS_PROTOCOL = AS0_METRICS_PROTOCOL
LOOKUP_N = 64
PEAK_N = 256
DECODE_N = 12
ABSTAIN_N = 32
METRICS_THESIS = (
    "Republish p50/p99 wall_ms for LOOKUP · PEAK · DECODE · ABSTAIN after "
    "ask-path changes + KB coverage % with explicit holes; LOOKUP wall=0 "
    "≠ speed IQ; no fake complete KB"
)


def telemetry_rules_ok(
    *,
    path: str,
    walls: Sequence[float],
    n_news: Sequence[int],
    modes: Sequence[str],
    product_modes: Sequence[str] | None = None,
) -> bool:
    """
    GIVEN AS0 metrics protocol rules
    WHEN checking a path sample set
    THEN True iff path telemetry matches LOOKUP|PEAK|DECODE|ABSTAIN charter.
    """
    if path not in METRICS_PATHS or not walls:
        return False
    pmodes = list(product_modes) if product_modes is not None else [
        map_as_product_mode(m) for m in modes
    ]
    if path == "LOOKUP":
        return all(pm == "LOOKUP" for pm in pmodes)
    if path == "PEAK":
        if not all(float(w) > 0.0 for w in walls):
            return False
        return all(pm == "PEAK" or "PEAK" in str(m).upper() for pm, m in zip(pmodes, modes))
    if path == "ABSTAIN":
        if not all(float(w) >= 0.0 for w in walls):
            return False
        return all(pm == "ABSTAIN" for pm in pmodes)
    # DECODE — neural tokens; measure with abstain=False
    if len(n_news) != len(walls):
        return False
    if not all(float(w) > 0.0 and int(n) > 0 for w, n in zip(walls, n_news)):
        return False
    return all(pm == "DECODE" for pm in pmodes)


def protocol_ok() -> bool:
    """True iff AS0 metrics protocol lists tetrad + p50/p99 + holes."""
    paths = METRICS_PROTOCOL.get("paths")
    metrics = METRICS_PROTOCOL.get("metrics")
    kb = METRICS_PROTOCOL.get("kb")
    if not isinstance(paths, list) or set(paths) != AS0_MODES:
        return False
    if not isinstance(metrics, list) or "p50_wall_ms" not in metrics:
        return False
    if "p99_wall_ms" not in metrics:
        return False
    if not isinstance(kb, list) or "coverage_pct" not in kb:
        return False
    if "hole_list" not in kb:
        return False
    return bool(METRICS_PROTOCOL.get("complete_claim_forbidden"))


def kb_gate_ok(snap: Mapping[str, Any]) -> bool:
    """
    GIVEN KB coverage snapshot
    WHEN applying AS5 hole honesty
    THEN True iff coverage_pct published, holes explicit, no fake complete.
    """
    if "coverage_pct" not in snap:
        return False
    if not bool(snap.get("complete_claim_forbidden")):
        return False
    holes = snap.get("holes")
    if not isinstance(holes, list) or len(holes) < 1:
        return False
    return all(h in holes for h in PRODUCT_HOLES)


def decide_metrics(
    *,
    paths: Mapping[str, Mapping[str, Any]],
    telemetry_ok: Mapping[str, bool],
    regress_noted: bool,
    snap: Mapping[str, Any],
) -> str:
    """
    GIVEN latency tetrad + KB snapshot
    WHEN applying pesquisa §5 AS5 gate
    THEN KILL if broken/silent regress/fake KB; else PROMOTE (publish).
    """
    if not protocol_ok():
        return "KILL (AS0 metrics protocol incomplete)"
    for path in METRICS_PATHS:
        if path not in paths:
            return f"KILL (missing path: {path})"
        st = paths[path]
        if "p50_wall_ms" not in st or "p99_wall_ms" not in st:
            return f"KILL (missing percentiles: {path})"
        if not bool(telemetry_ok.get(path)):
            return f"KILL (telemetry broken: {path})"
    peak_p50 = float(paths["PEAK"]["p50_wall_ms"])
    if peak_regressed(peak_p50) and not regress_noted:
        return "KILL (PEAK regress vs FASTBASE hot without note)"
    if not kb_gate_ok(snap):
        return "KILL (KB holes / coverage honesty failed)"
    return "PROMOTE"
