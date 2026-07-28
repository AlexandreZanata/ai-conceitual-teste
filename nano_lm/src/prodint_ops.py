"""Wave AY1 H-PRODINT: close intent/adversary FH; hold hard-natural; publish metrics."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ay_session_ops import (
    AY0_ANTI_FP,
    AY0_INTENT_FP_ROWS,
    AY0_MODES,
    AY0_PRODUCT_INT_CHARTER,
    AY0_SAFE_NOTE,
    AY0_SHIP_LOCK,
    map_ay_product_mode,
)
from ax_session_ops import AX0_HARD_NATURAL_ROWS
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
    "PRODINT_ID",
    "PRODINT_THESIS",
    "PRODINT_CLAIM",
    "PRODINT_SAFE_NOTE",
    "PRODINT_ANTI_FP",
    "INTENT_FP_ROWS",
    "HARD_NATURAL_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "bars_from_int_charter",
    "intent_row_ok",
    "intent_false_hit",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "decode_content_honest",
    "gate_junk_decode",
    "map_ay_product_mode",
    "extract_prodint_board",
    "decide_prodint",
]

PRODINT_ID = "H-PRODINT"
PRODINT_THESIS = (
    "Close intent/adversary false-hit debt on Caminho A: intent FH 0 on "
    "live FP class (mul≠add · diff≠sum · remove≠clear · half-known BIP); "
    "hold hard-natural ≥ bar; FH 0 near-miss; DECODE usable or ABSTAIN; "
    "publish para · FH · p50/p99 · KB · modes 4/4 — no bank stuffing"
)
PRODINT_CLAIM = AY0_SHIP_LOCK
PRODINT_SAFE_NOTE = AY0_SAFE_NOTE
PRODINT_ANTI_FP = AY0_ANTI_FP
INTENT_FP_ROWS = AY0_INTENT_FP_ROWS
HARD_NATURAL_ROWS = AX0_HARD_NATURAL_ROWS


def bars_from_int_charter(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AY0 product-int charter
    WHEN reading bars
    THEN return typed bar dict for PRODINT gate.
    """
    src = suite if suite is not None else AY0_PRODUCT_INT_CHARTER
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
    modes = sorted(str(k) for k in paths.keys() if str(k) in AY0_MODES)
    if len(modes) >= 4:
        return modes
    arms = list(ship.get("arms") or [])
    return sorted(
        {
            str(a.get("product_mode") or "")
            for a in arms
            if str(a.get("product_mode") or "") in AY0_MODES
        }
    )


def intent_false_hit(row: Mapping[str, Any]) -> bool:
    """
    GIVEN intent-FP ask result
    WHEN product mode is LOOKUP
    THEN True (intent-mismatch LOOKUP = false-hit).
    """
    mode = str(row.get("product_mode") or map_ay_product_mode(str(row.get("mode", ""))))
    return mode == "LOOKUP"


def intent_row_ok(row: Mapping[str, Any]) -> bool:
    """
    GIVEN intent-FP ask result
    WHEN expect ABSTAIN
    THEN True iff product mode is ABSTAIN (not LOOKUP false-hit).
    """
    mode = str(row.get("product_mode") or map_ay_product_mode(str(row.get("mode", ""))))
    return mode == "ABSTAIN"


def extract_prodint_board(
    *,
    intent_rows: Sequence[Mapping[str, Any]],
    para_hits: Sequence[bool],
    near: Mapping[str, Any],
    peak: Mapping[str, Any],
    known: Mapping[str, Any],
    decode: Mapping[str, Any],
    metrics: Mapping[str, Any],
    ship: Mapping[str, Any],
) -> dict[str, Any]:
    """
    GIVEN live intent-FP + hard-natural measurements + metrics/ship
    WHEN building PRODINT board
    THEN publish intent FH · hard-natural hold · FH · DECODE · latency · KB · modes.
    """
    n_intent = len(intent_rows)
    n_fh = int(sum(1 for r in intent_rows if intent_false_hit(r)))
    n_ok = int(sum(1 for r in intent_rows if intent_row_ok(r)))
    n_para = len(para_hits)
    n_para_true = int(sum(1 for h in para_hits if h))
    para_hit = float(n_para_true / n_para) if n_para else 0.0
    nm_ok = near_miss_ok(near)
    coverage, holes = _kb_from_metrics(metrics)
    modes = _modes_visible(metrics, ship)
    return {
        "intent_false_hit": n_fh,
        "intent_ok_n": n_ok,
        "intent_n": n_intent,
        "intent_abstain_rate": float(n_ok / n_intent) if n_intent else 0.0,
        "hard_natural_para_hit": para_hit,
        "para_n_true": n_para_true,
        "para_n": n_para,
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
        "pack_fh_neq_live_intent": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }


def _gate_intent_bars(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    fh_max = int(bar.get("intent_false_hit_max", 0))
    fh = int(board.get("intent_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (intent_false_hit {fh} > {fh_max})"
    min_n = int(bar.get("intent_fp_min_n", 12))
    if int(board.get("intent_n") or 0) < min_n:
        return f"KILL (intent-fp n {board.get('intent_n')} < {min_n})"
    if int(board.get("intent_ok_n") or 0) < int(board.get("intent_n") or 0):
        return (
            f"HOLD (intent ABSTAIN {board.get('intent_ok_n')}/"
            f"{board.get('intent_n')} incomplete)"
        )
    if not bool(bar.get("bank_stuff_forbidden", True)):
        return "KILL (bank stuffing must stay forbidden)"
    if not bool(bar.get("pack_fh_neq_live_intent", True)):
        return "KILL (pack FH ≠ live intent bar missing)"
    return None


def _gate_core_bars(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    if not bool(bar.get("regression_hold", True)):
        return "KILL (product-int must require regression_hold)"
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
    modes_req = set(bar.get("modes_required") or list(AY0_MODES))
    modes = set(board.get("modes_visible") or [])
    if modes_req and modes != modes_req:
        return f"KILL (modes visible {sorted(modes)} ≠ {sorted(modes_req)})"
    if not board.get("latency"):
        return "KILL (latency p50/p99 not published)"
    if board.get("kb_coverage_pct") is None:
        return "KILL (KB coverage not published)"
    if not bool(bar.get("decode_gibberish_neq_content_ok", True)):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    return None


def decide_prodint(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN PRODINT metrics board
    WHEN applying pesquisa §5 AY1
    THEN PROMOTE iff intent FH 0 + hard-natural hold; else KILL/HOLD.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_int_charter()
    err = (
        _gate_intent_bars(board, bar)
        or _gate_core_bars(board, bar)
        or _gate_para_modes(board, bar)
    )
    if err:
        return err
    return (
        f"PROMOTE ({PRODINT_ID}: intent FH 0 on live FP class; "
        "hard-natural hold; no bank stuffing)"
    )
