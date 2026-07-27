"""Wave AT1 H-PRODREG: Caminho A product regression vs AT0/AS bars."""

from __future__ import annotations

from typing import Any, Mapping

from at_session_ops import AT0_ANTI_FP, AT0_PRODREG_SUITE, AT0_SAFE_NOTE

__all__ = [
    "PRODREG_ID",
    "PRODREG_THESIS",
    "PRODREG_CLAIM",
    "PRODREG_PILLARS",
    "PRODREG_SAFE_NOTE",
    "PRODREG_ANTI_FP",
    "bars_from_suite",
    "pillar_pass",
    "extract_prodreg_metrics",
    "decide_prodreg",
]

PRODREG_ID = "H-PRODREG"
PRODREG_THESIS = (
    "Caminho A regression: remeasure para hit · FH · p50/p99 · KB holes · "
    "modes · default-ask abstain against AT0/AS bars; PROMOTE iff all hold"
)
PRODREG_CLAIM = (
    "AF packaged stack + AQ product layer + AS trust path — not open chat LM"
)
PRODREG_PILLARS: tuple[str, ...] = (
    "askabstain",
    "advsafe",
    "paraext2",
    "metrics",
    "shipui",
)
PRODREG_SAFE_NOTE = AT0_SAFE_NOTE
PRODREG_ANTI_FP = AT0_ANTI_FP


def bars_from_suite(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AT0 PRODREG suite
    WHEN reading bars
    THEN return typed bar dict for gate checks.
    """
    src = suite if suite is not None else AT0_PRODREG_SUITE
    bars = src.get("bars")
    if not isinstance(bars, dict):
        return {}
    return dict(bars)


def pillar_pass(decision: str) -> bool:
    """True iff pillar decision string starts with PROMOTE."""
    return str(decision).startswith("PROMOTE")


def extract_prodreg_metrics(
    *,
    para: Mapping[str, Any],
    adv: Mapping[str, Any],
    metrics: Mapping[str, Any],
    ask: Mapping[str, Any],
    ship: Mapping[str, Any],
) -> dict[str, Any]:
    """
    GIVEN pillar runner summaries
    WHEN extracting published Caminho A numbers
    THEN return para_hit · false_hit · latency · KB · modes · abstain.
    """
    pstats = dict(para.get("stats") or {})
    astats = dict(adv.get("stats") or {})
    ask_stats = dict(ask.get("stats") or {})
    paths = dict(metrics.get("paths") or {})
    latency: dict[str, Any] = {}
    for name, row in paths.items():
        stats = dict(row.get("stats") or {})
        latency[str(name)] = {
            "p50_wall_ms": stats.get("p50_wall_ms"),
            "p99_wall_ms": stats.get("p99_wall_ms"),
        }
    kb = dict(metrics.get("kb") or {})
    snap = dict(kb.get("snap") or kb)
    kb_hole_list = list(
        snap.get("holes")
        or snap.get("hole_list")
        or snap.get("product_holes")
        or kb.get("holes")
        or []
    )
    arms = list(ship.get("arms") or [])
    modes = sorted(
        {
            str(a.get("product_mode") or "")
            for a in arms
            if str(a.get("product_mode") or "")
        }
    )
    return {
        "para_hit": float(pstats.get("hit_rate") or 0.0),
        "para_n_true": int(pstats.get("n_true_hit") or 0),
        "para_n": int(pstats.get("n_trials") or 0),
        "false_hit": int(astats.get("n_false_hit") or 0),
        "false_hit_ids": list(adv.get("false_hit_ids") or []),
        "latency": latency,
        "kb_coverage_pct": snap.get("coverage_pct"),
        "kb_hole_list": kb_hole_list,
        "modes_visible": modes,
        "modes_n": len(modes),
        "default_ask_abstain_rate": float(
            ask_stats.get("ood_abstain_rate")
            or ask_stats.get("abstain_rate")
            or 0.0
        ),
        "askabstain_known_ok": bool(ask_stats.get("known_lookup_ok")),
    }


def _hard_kill_pillar(name: str, dec: str) -> str | None:
    if pillar_pass(dec):
        return None
    if str(dec).startswith("KILL"):
        return f"KILL ({name}: {dec})"
    if str(dec).startswith("HOLD"):
        # Soft deepen on para → HOLD; hard pillars → KILL if not PROMOTE.
        if name == "paraext2":
            return f"HOLD ({name}: {dec})"
        return f"KILL ({name} not PROMOTE: {dec})"
    return f"KILL ({name} missing/unknown: {dec})"


def decide_prodreg(
    *,
    pillars: Mapping[str, str],
    metrics_board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN pillar decisions + published metrics
    WHEN applying pesquisa §5 AT1 H-PRODREG
    THEN PROMOTE iff AS/AT0 bars hold; FH>0 or core fail → KILL;
         para soft HOLD possible; unsigned anti-FP → KILL.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_suite()
    for name in PRODREG_PILLARS:
        err = _hard_kill_pillar(name, str(pillars.get(name, "MISSING")))
        if err:
            return err
    fh_max = int(bar.get("false_hit_max", 0))
    fh = int(metrics_board.get("false_hit") or 0)
    if fh > fh_max:
        return f"KILL (false_hit {fh} > {fh_max})"
    para_min = float(bar.get("para_hit_min", 0.70))
    para = float(metrics_board.get("para_hit") or 0.0)
    if para < para_min:
        return f"HOLD (para_hit {para:.2f} < {para_min})"
    modes_req = set(bar.get("modes_required") or [])
    modes = set(metrics_board.get("modes_visible") or [])
    if modes_req and modes != modes_req:
        return f"KILL (modes visible {sorted(modes)} ≠ {sorted(modes_req)})"
    if not metrics_board.get("latency"):
        return "KILL (latency p50/p99 not published)"
    if metrics_board.get("kb_coverage_pct") is None:
        return "KILL (KB coverage not published)"
    return f"PROMOTE ({PRODREG_ID}: all Caminho A bars hold)"
