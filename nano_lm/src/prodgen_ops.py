"""Wave AZ1 H-PRODGEN: held-out FH 0 · no over-refuse · hold AY/AX · metrics."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ax_session_ops import AX0_HARD_NATURAL_ROWS
from ay_session_ops import AY0_INTENT_FP_ROWS
from az_session_ops import (
    AZ0_ANTI_FP,
    AZ0_HELDOUT_FP_ROWS,
    AZ0_MODES,
    AZ0_OVERREFUSE_ROWS,
    AZ0_PRODUCT_GEN_CHARTER,
    AZ0_SAFE_NOTE,
    AZ0_SHIP_LOCK,
    map_az_product_mode,
)
from prodhard_ops import KNOWN_ASK, NEAR_MISS_ASK, PEAK_ASK
from prodint_ops import intent_false_hit, intent_row_ok
from prodship_ops import (
    DECODE_PROBE_ASK,
    decode_content_honest,
    gate_junk_decode,
    human_para_hit,
    near_miss_ok,
    peak_ok,
)

__all__ = [
    "PRODGEN_ID",
    "PRODGEN_THESIS",
    "PRODGEN_CLAIM",
    "PRODGEN_SAFE_NOTE",
    "PRODGEN_ANTI_FP",
    "HELDOUT_FP_ROWS",
    "OVERREFUSE_ROWS",
    "NAMED_INTENT_ROWS",
    "HARD_NATURAL_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "bars_from_gen_charter",
    "intent_row_ok",
    "intent_false_hit",
    "overrefuse_miss",
    "overrefuse_row_ok",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "decode_content_honest",
    "gate_junk_decode",
    "map_az_product_mode",
    "extract_prodgen_board",
    "decide_prodgen",
]

PRODGEN_ID = "H-PRODGEN"
PRODGEN_THESIS = (
    "Close held-out intent FH + over-refuse on Caminho A: held-out FH 0 "
    "(div≠add · sub≠add · wrong-slot BIP); exact clear gold LOOKUP; "
    "hold AY named intent FH 0 + hard-natural ≥ bar; FH 0 near-miss; "
    "DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · "
    "modes 4/4 — no bank stuffing"
)
PRODGEN_CLAIM = AZ0_SHIP_LOCK
PRODGEN_SAFE_NOTE = AZ0_SAFE_NOTE
PRODGEN_ANTI_FP = AZ0_ANTI_FP
HELDOUT_FP_ROWS = AZ0_HELDOUT_FP_ROWS
OVERREFUSE_ROWS = AZ0_OVERREFUSE_ROWS
NAMED_INTENT_ROWS = AY0_INTENT_FP_ROWS
HARD_NATURAL_ROWS = AX0_HARD_NATURAL_ROWS


def bars_from_gen_charter(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AZ0 product-gen charter
    WHEN reading bars
    THEN return typed bar dict for PRODGEN gate.
    """
    src = suite if suite is not None else AZ0_PRODUCT_GEN_CHARTER
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def overrefuse_miss(row: Mapping[str, Any]) -> bool:
    """
    GIVEN exact-clear over-refuse probe
    WHEN product mode is not LOOKUP (or gold missing)
    THEN True (exact-gold ABSTAIN = product miss).
    """
    return not overrefuse_row_ok(row)


def overrefuse_row_ok(row: Mapping[str, Any]) -> bool:
    """
    GIVEN exact-clear ask result
    WHEN expect LOOKUP a.clear()
    THEN True iff LOOKUP and completion contains clear.
    """
    mode = str(
        row.get("product_mode") or map_az_product_mode(str(row.get("mode", "")))
    )
    if mode != "LOOKUP":
        return False
    return "clear" in str(row.get("completion", "")).lower()


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
    modes = sorted(str(k) for k in paths.keys() if str(k) in AZ0_MODES)
    if len(modes) >= 4:
        return modes
    arms = list(ship.get("arms") or [])
    return sorted(
        {
            str(a.get("product_mode") or "")
            for a in arms
            if str(a.get("product_mode") or "") in AZ0_MODES
        }
    )


def extract_prodgen_board(
    *,
    heldout_rows: Sequence[Mapping[str, Any]],
    overrefuse_rows: Sequence[Mapping[str, Any]],
    named_rows: Sequence[Mapping[str, Any]],
    para_hits: Sequence[bool],
    near: Mapping[str, Any],
    peak: Mapping[str, Any],
    known: Mapping[str, Any],
    decode: Mapping[str, Any],
    metrics: Mapping[str, Any],
    ship: Mapping[str, Any],
) -> dict[str, Any]:
    """
    GIVEN held-out + over-refuse + named + hard-natural measurements
    WHEN building PRODGEN board
    THEN publish held-out FH · over-refuse miss · named hold · latency · KB · modes.
    """
    n_h = len(heldout_rows)
    n_h_fh = int(sum(1 for r in heldout_rows if intent_false_hit(r)))
    n_h_ok = int(sum(1 for r in heldout_rows if intent_row_ok(r)))
    n_o = len(overrefuse_rows)
    n_o_miss = int(sum(1 for r in overrefuse_rows if overrefuse_miss(r)))
    n_o_ok = int(sum(1 for r in overrefuse_rows if overrefuse_row_ok(r)))
    n_n = len(named_rows)
    n_n_fh = int(sum(1 for r in named_rows if intent_false_hit(r)))
    n_n_ok = int(sum(1 for r in named_rows if intent_row_ok(r)))
    n_para = len(para_hits)
    n_para_true = int(sum(1 for h in para_hits if h))
    para_hit = float(n_para_true / n_para) if n_para else 0.0
    nm_ok = near_miss_ok(near)
    coverage, holes = _kb_from_metrics(metrics)
    modes = _modes_visible(metrics, ship)
    return {
        "heldout_false_hit": n_h_fh,
        "heldout_ok_n": n_h_ok,
        "heldout_n": n_h,
        "heldout_abstain_rate": float(n_h_ok / n_h) if n_h else 0.0,
        "overrefuse_miss": n_o_miss,
        "overrefuse_ok_n": n_o_ok,
        "overrefuse_n": n_o,
        "named_intent_false_hit": n_n_fh,
        "named_ok_n": n_n_ok,
        "named_n": n_n,
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
        "named_fh_neq_heldout": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }


def _gate_heldout(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    fh_max = int(bar.get("heldout_false_hit_max", 0))
    fh = int(board.get("heldout_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (heldout_false_hit {fh} > {fh_max})"
    min_n = int(bar.get("heldout_fp_min_n", 12))
    if int(board.get("heldout_n") or 0) < min_n:
        return f"KILL (heldout-fp n {board.get('heldout_n')} < {min_n})"
    if int(board.get("heldout_ok_n") or 0) < int(board.get("heldout_n") or 0):
        return (
            f"HOLD (heldout ABSTAIN {board.get('heldout_ok_n')}/"
            f"{board.get('heldout_n')} incomplete)"
        )
    return None


def _gate_overrefuse(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    miss_max = int(bar.get("overrefuse_miss_max", 0))
    miss = int(board.get("overrefuse_miss") or 0)
    if miss > miss_max:
        return f"KILL (overrefuse_miss {miss} > {miss_max})"
    min_n = int(bar.get("overrefuse_min_n", 3))
    if int(board.get("overrefuse_n") or 0) < min_n:
        return f"KILL (overrefuse n {board.get('overrefuse_n')} < {min_n})"
    if int(board.get("overrefuse_ok_n") or 0) < int(board.get("overrefuse_n") or 0):
        return (
            f"HOLD (overrefuse LOOKUP {board.get('overrefuse_ok_n')}/"
            f"{board.get('overrefuse_n')} incomplete)"
        )
    return None


def _gate_named_hold(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    fh_max = int(bar.get("named_intent_false_hit_max", 0))
    fh = int(board.get("named_intent_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (named_intent_false_hit {fh} > {fh_max})"
    if int(board.get("named_n") or 0) < 12:
        return f"KILL (named intent n {board.get('named_n')} < 12)"
    if int(board.get("named_ok_n") or 0) < int(board.get("named_n") or 0):
        return (
            f"HOLD (named ABSTAIN {board.get('named_ok_n')}/"
            f"{board.get('named_n')} incomplete)"
        )
    return None


def _gate_core(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    if not bool(bar.get("bank_stuff_forbidden", True)):
        return "KILL (bank stuffing must stay forbidden)"
    if not bool(bar.get("named_fh_neq_heldout", True)):
        return "KILL (named FH ≠ held-out bar missing)"
    if not bool(bar.get("regression_hold", True)):
        return "KILL (product-gen must require regression_hold)"
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
    modes_req = set(bar.get("modes_required") or list(AZ0_MODES))
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


def decide_prodgen(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN PRODGEN metrics board
    WHEN applying pesquisa §5 AZ1
    THEN PROMOTE iff held-out FH 0 + over-refuse 0 + AY/AX hold.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_gen_charter()
    err = (
        _gate_heldout(board, bar)
        or _gate_overrefuse(board, bar)
        or _gate_named_hold(board, bar)
        or _gate_core(board, bar)
        or _gate_para_modes(board, bar)
    )
    if err:
        return err
    return (
        f"PROMOTE ({PRODGEN_ID}: held-out FH 0; over-refuse 0; "
        "AY named + hard-natural hold; no bank stuffing)"
    )
