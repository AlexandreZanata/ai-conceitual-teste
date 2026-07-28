"""Wave AX1 H-PRODNAT: close hard-natural para debt; publish product metrics."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ax_session_ops import (
    AX0_ANTI_FP,
    AX0_HARD_NATURAL_ROWS,
    AX0_MODES,
    AX0_PRODUCT_NAT_CHARTER,
    AX0_SAFE_NOTE,
    AX0_SHIP_LOCK,
)
from prodhard_ops import KNOWN_ASK, NEAR_MISS_ASK, PEAK_ASK
from prodship_ops import (
    DECODE_PROBE_ASK,
    decode_content_honest,
    gate_junk_decode,
    human_para_hit,
    near_miss_ok,
    peak_ok,
)

__all__ = [
    "PRODNAT_ID",
    "PRODNAT_THESIS",
    "PRODNAT_CLAIM",
    "PRODNAT_SAFE_NOTE",
    "PRODNAT_ANTI_FP",
    "HARD_NATURAL_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "bars_from_nat_charter",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "decode_content_honest",
    "gate_junk_decode",
    "extract_prodnat_board",
    "decide_prodnat",
]

PRODNAT_ID = "H-PRODNAT"
PRODNAT_THESIS = (
    "Close hard-natural human para debt on Caminho A: hard-natural ≥ bar; "
    "FH 0; DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · "
    "modes 4/4; pack-para ≠ hard-natural coverage claim"
)
PRODNAT_CLAIM = AX0_SHIP_LOCK
PRODNAT_SAFE_NOTE = AX0_SAFE_NOTE
PRODNAT_ANTI_FP = AX0_ANTI_FP
HARD_NATURAL_ROWS = AX0_HARD_NATURAL_ROWS


def bars_from_nat_charter(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AX0 product-nat charter
    WHEN reading bars
    THEN return typed bar dict for PRODNAT gate.
    """
    src = suite if suite is not None else AX0_PRODUCT_NAT_CHARTER
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def _latency_from_metrics(metrics: Mapping[str, Any]) -> dict[str, Any]:
    paths = dict(metrics.get("paths") or {})
    latency: dict[str, Any] = {}
    for name, row in paths.items():
        stats = dict(row.get("stats") or {})
        latency[str(name)] = {
            "p50_wall_ms": stats.get("p50_wall_ms"),
            "p99_wall_ms": stats.get("p99_wall_ms"),
        }
    return latency


def _kb_from_metrics(metrics: Mapping[str, Any]) -> tuple[Any, list[Any]]:
    kb = dict(metrics.get("kb") or {})
    snap = dict(kb.get("snap") or kb)
    holes = list(
        snap.get("holes")
        or snap.get("hole_list")
        or snap.get("product_holes")
        or kb.get("holes")
        or []
    )
    return snap.get("coverage_pct"), holes


def _modes_visible(
    metrics: Mapping[str, Any], ship: Mapping[str, Any]
) -> list[str]:
    paths = dict(metrics.get("paths") or {})
    modes = sorted(str(k) for k in paths.keys() if str(k) in AX0_MODES)
    if len(modes) >= 4:
        return modes
    arms = list(ship.get("arms") or [])
    return sorted(
        {
            str(a.get("product_mode") or "")
            for a in arms
            if str(a.get("product_mode") or "") in AX0_MODES
        }
    )


def extract_prodnat_board(
    *,
    para_hits: Sequence[bool],
    near: Mapping[str, Any],
    peak: Mapping[str, Any],
    known: Mapping[str, Any],
    decode: Mapping[str, Any],
    metrics: Mapping[str, Any],
    ship: Mapping[str, Any],
) -> dict[str, Any]:
    """
    GIVEN live hard-natural measurements + metrics/ship summaries
    WHEN building PRODNAT board
    THEN publish hard-natural · FH · DECODE · latency · KB · modes.
    """
    n = len(para_hits)
    n_true = int(sum(1 for h in para_hits if h))
    para_hit = float(n_true / n) if n else 0.0
    nm_ok = near_miss_ok(near)
    coverage, holes = _kb_from_metrics(metrics)
    modes = _modes_visible(metrics, ship)
    return {
        "hard_natural_para_hit": para_hit,
        "para_n_true": n_true,
        "para_n": n,
        "false_hit": 0 if nm_ok else 1,
        "near_miss_ok": nm_ok,
        "near_miss_mode": near.get("product_mode") or near.get("mode"),
        "peak_ok": peak_ok(peak),
        "peak_mode": peak.get("product_mode") or peak.get("mode"),
        "peak_completion": str(peak.get("completion", ""))[:160],
        "known_lookup_ok": human_para_hit(known),
        "decode_content_ok": decode_content_honest(decode),
        "decode_mode": decode.get("product_mode") or decode.get("mode"),
        "decode_completion": str(decode.get("completion", ""))[:160],
        "decode_abstained": bool(decode.get("abstained")),
        "latency": _latency_from_metrics(metrics),
        "kb_coverage_pct": coverage,
        "kb_hole_list": holes,
        "modes_visible": modes,
        "modes_n": len(modes),
        "pressure_para_neq_hard_natural": True,
        "regression_hold": True,
    }


def _gate_core_bars(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    if not bool(bar.get("regression_hold", True)):
        return "KILL (product-nat must require regression_hold)"
    if not bool(board.get("near_miss_ok")):
        return "KILL (near-miss on default ask not ABSTAIN)"
    fh_max = int(bar.get("false_hit_max", 0))
    fh = int(board.get("false_hit") or 0)
    if fh > fh_max:
        return f"KILL (false_hit {fh} > {fh_max})"
    if not bool(board.get("decode_content_ok")):
        return "KILL (DECODE gibberish still content_ok / not abstained)"
    if not bool(board.get("known_lookup_ok")):
        return "KILL (known LOOKUP regress)"
    if not bool(board.get("peak_ok")):
        return "KILL (PEAK not usable and not ABSTAIN)"
    return None


def _gate_para_modes(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    para_min = float(bar.get("hard_natural_para_hit_min", 0.70))
    para = float(board.get("hard_natural_para_hit") or 0.0)
    if para < para_min:
        return f"HOLD (hard_natural_para_hit {para:.2f} < {para_min})"
    min_n = int(bar.get("hard_natural_min_n", 15))
    if int(board.get("para_n") or 0) < min_n:
        return f"KILL (hard natural n {board.get('para_n')} < {min_n})"
    modes_req = set(bar.get("modes_required") or list(AX0_MODES))
    modes = set(board.get("modes_visible") or [])
    if modes_req and modes != modes_req:
        return f"KILL (modes visible {sorted(modes)} ≠ {sorted(modes_req)})"
    if not board.get("latency"):
        return "KILL (latency p50/p99 not published)"
    if board.get("kb_coverage_pct") is None:
        return "KILL (KB coverage not published)"
    if not bool(bar.get("pressure_para_neq_hard_natural", True)):
        return "KILL (pressure-para ≠ hard-natural bar missing)"
    if not bool(bar.get("decode_gibberish_neq_content_ok", True)):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    return None


def decide_prodnat(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN PRODNAT metrics board
    WHEN applying pesquisa §5 AX1
    THEN PROMOTE iff hard-natural bars hold; else KILL/HOLD.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_nat_charter()
    err = _gate_core_bars(board, bar) or _gate_para_modes(board, bar)
    if err:
        return err
    return (
        f"PROMOTE ({PRODNAT_ID}: hard-natural Caminho A bars held; "
        "pack-para ≠ hard-natural coverage)"
    )
