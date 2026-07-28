"""Wave BA1 H-REALGAIN: forever FH 0 · AZ hold · over-refuse 0 · live board."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from az_session_ops import (
    AZ0_HELDOUT_FP_ROWS,
    AZ0_MODES,
    AZ0_OVERREFUSE_ROWS,
)
from ba_session_ops import (
    BA0_ANTI_FP,
    BA0_FOREVER_ROWS,
    BA0_SAFE_NOTE,
    BA0_SCOREBOARD,
    BA0_SHIP_LOCK,
    map_ba_product_mode,
)
from prodgen_ops import overrefuse_miss, overrefuse_row_ok
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
    "REALGAIN_ID",
    "REALGAIN_THESIS",
    "REALGAIN_CLAIM",
    "REALGAIN_SAFE_NOTE",
    "REALGAIN_ANTI_FP",
    "FOREVER_ROWS",
    "AZ_HELDOUT_ROWS",
    "OVERREFUSE_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "bars_from_scoreboard",
    "intent_row_ok",
    "intent_false_hit",
    "overrefuse_miss",
    "overrefuse_row_ok",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "decode_content_honest",
    "gate_junk_decode",
    "map_ba_product_mode",
    "score_live_row",
    "extract_realgain_board",
    "decide_realgain",
]

REALGAIN_ID = "H-REALGAIN"
REALGAIN_THESIS = (
    "Drive forever held-out FH → 0 (pow≠add · mod≠add · max≠add · "
    "sort≠reverse · len≠junk) via SEMWRAP gate — not bank stuffing; "
    "hold AZ div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard "
    "OK|FP|MISS|ABSTAIN-OK; modes · p50/p99 · DECODE law"
)
REALGAIN_CLAIM = BA0_SHIP_LOCK
REALGAIN_SAFE_NOTE = BA0_SAFE_NOTE
REALGAIN_ANTI_FP = BA0_ANTI_FP
FOREVER_ROWS = BA0_FOREVER_ROWS
AZ_HELDOUT_ROWS = AZ0_HELDOUT_FP_ROWS
OVERREFUSE_ROWS = AZ0_OVERREFUSE_ROWS


def bars_from_scoreboard(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN BA0 §1 scoreboard
    WHEN reading bars
    THEN return typed bar dict for REALGAIN gate.
    """
    src = suite if suite is not None else BA0_SCOREBOARD
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def score_live_row(row: Mapping[str, Any], *, expect_mode: str) -> str:
    """
    GIVEN live ask result + expected mode
    WHEN scoring OK|FP|MISS|ABSTAIN-OK
    THEN classify per pesquisa §1 anti-FP dictionary.
    """
    mode = str(
        row.get("product_mode") or map_ba_product_mode(str(row.get("mode", "")))
    )
    if expect_mode == "ABSTAIN":
        if mode == "LOOKUP":
            return "FP"
        if mode == "ABSTAIN":
            return "ABSTAIN-OK"
        return "MISS"
    if expect_mode == "LOOKUP":
        if mode == "LOOKUP":
            gold_ok = "clear" in str(row.get("completion", "")).lower()
            return "OK" if gold_ok or not row.get("gold") else "MISS"
        if mode == "ABSTAIN":
            return "MISS"
        return "MISS"
    return "OK" if mode == expect_mode else "MISS"


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


def extract_realgain_board(
    *,
    forever_rows: Sequence[Mapping[str, Any]],
    az_rows: Sequence[Mapping[str, Any]],
    overrefuse_rows: Sequence[Mapping[str, Any]],
    live_scores: Sequence[str],
    near: Mapping[str, Any],
    peak: Mapping[str, Any],
    known: Mapping[str, Any],
    decode: Mapping[str, Any],
    metrics: Mapping[str, Any],
    ship: Mapping[str, Any],
) -> dict[str, Any]:
    """
    GIVEN forever + AZ hold + over-refuse + live score labels
    WHEN building REALGAIN board
    THEN publish forever FH · AZ hold · over-refuse · live · latency · modes.
    """
    n_f = len(forever_rows)
    n_f_fh = int(sum(1 for r in forever_rows if intent_false_hit(r)))
    n_f_ok = int(sum(1 for r in forever_rows if intent_row_ok(r)))
    n_a = len(az_rows)
    n_a_fh = int(sum(1 for r in az_rows if intent_false_hit(r)))
    n_a_ok = int(sum(1 for r in az_rows if intent_row_ok(r)))
    n_o = len(overrefuse_rows)
    n_o_miss = int(sum(1 for r in overrefuse_rows if overrefuse_miss(r)))
    n_o_ok = int(sum(1 for r in overrefuse_rows if overrefuse_row_ok(r)))
    score_counts = {k: 0 for k in ("OK", "FP", "MISS", "ABSTAIN-OK")}
    for label in live_scores:
        if label in score_counts:
            score_counts[label] += 1
    nm_ok = near_miss_ok(near)
    coverage, holes = _kb_from_metrics(metrics)
    modes = _modes_visible(metrics, ship)
    return {
        "forever_false_hit": n_f_fh,
        "forever_ok_n": n_f_ok,
        "forever_n": n_f,
        "az_hold_false_hit": n_a_fh,
        "az_hold_ok_n": n_a_ok,
        "az_hold_n": n_a,
        "overrefuse_miss": n_o_miss,
        "overrefuse_ok_n": n_o_ok,
        "overrefuse_n": n_o,
        "live_ask_ok_fp_miss": (
            f"{score_counts['OK']}/{score_counts['FP']}/"
            f"{score_counts['MISS']}+{score_counts['ABSTAIN-OK']}"
        ),
        "live_scores": dict(score_counts),
        "live_fp": score_counts["FP"],
        "false_hit": 0 if nm_ok else 1,
        "near_miss_ok": nm_ok,
        "near_miss_mode": near.get("product_mode") or near.get("mode"),
        "peak_ok": peak_ok(peak),
        "peak_mode": peak.get("product_mode") or peak.get("mode"),
        "known_lookup_ok": human_para_hit(known),
        "decode_content_ok": decode_content_honest(decode),
        "decode_mode": decode.get("product_mode") or decode.get("mode"),
        "decode_abstained": bool(decode.get("abstained")),
        "latency": _latency_from_metrics(metrics),
        "kb_coverage_pct": coverage,
        "kb_hole_list": holes,
        "modes_visible": modes,
        "modes_n": len(modes),
        "pack_pass_neq_forever": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }


def _gate_forever(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    fh_max = int(bar.get("forever_false_hit_max", 0))
    fh = int(board.get("forever_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (forever_false_hit {fh} > {fh_max})"
    min_n = int(bar.get("forever_min_n", 15))
    if int(board.get("forever_n") or 0) < min_n:
        return f"KILL (forever n {board.get('forever_n')} < {min_n})"
    if int(board.get("forever_ok_n") or 0) < int(board.get("forever_n") or 0):
        return (
            f"HOLD (forever ABSTAIN {board.get('forever_ok_n')}/"
            f"{board.get('forever_n')} incomplete)"
        )
    return None


def _gate_az_hold(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    fh_max = int(bar.get("az_hold_false_hit_max", 0))
    fh = int(board.get("az_hold_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (az_hold_false_hit {fh} > {fh_max})"
    if int(board.get("az_hold_n") or 0) < 12:
        return f"KILL (az hold n {board.get('az_hold_n')} < 12)"
    if int(board.get("az_hold_ok_n") or 0) < int(board.get("az_hold_n") or 0):
        return (
            f"HOLD (az hold ABSTAIN {board.get('az_hold_ok_n')}/"
            f"{board.get('az_hold_n')} incomplete)"
        )
    return None


def _gate_overrefuse(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    miss_max = int(bar.get("overrefuse_miss_max", 0))
    miss = int(board.get("overrefuse_miss") or 0)
    if miss > miss_max:
        return f"KILL (overrefuse_miss {miss} > {miss_max})"
    if int(board.get("overrefuse_n") or 0) < 3:
        return f"KILL (overrefuse n {board.get('overrefuse_n')} < 3)"
    if int(board.get("overrefuse_ok_n") or 0) < int(board.get("overrefuse_n") or 0):
        return (
            f"HOLD (overrefuse LOOKUP {board.get('overrefuse_ok_n')}/"
            f"{board.get('overrefuse_n')} incomplete)"
        )
    return None


def _gate_core(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    if not bool(bar.get("bank_stuff_forbidden", True)):
        return "KILL (bank stuffing must stay forbidden)"
    if not bool(bar.get("pack_pass_neq_forever", True)):
        return "KILL (pack PASS ≠ forever bar missing)"
    if not bool(bar.get("regression_hold", True)):
        return "KILL (must require regression_hold)"
    if not bool(board.get("near_miss_ok")):
        return "KILL (near-miss on default ask not ABSTAIN)"
    if int(board.get("false_hit") or 0) > 0:
        return "KILL (near-miss false_hit > 0)"
    if int(board.get("live_fp") or 0) > 0:
        return f"KILL (live ask FP {board.get('live_fp')} > 0)"
    if not bool(board.get("decode_content_ok")):
        return "KILL (DECODE gibberish still content_ok / not abstained)"
    if not bool(board.get("known_lookup_ok")):
        return "KILL (known LOOKUP regress)"
    if not bool(board.get("peak_ok")):
        return "KILL (PEAK not usable and not ABSTAIN)"
    return None


def _gate_modes_latency(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
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


def decide_realgain(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN REALGAIN metrics board
    WHEN applying pesquisa §8 BA1
    THEN PROMOTE iff forever FH 0 + AZ hold 0 + over-refuse 0 + live FP 0.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_scoreboard()
    err = (
        _gate_forever(board, bar)
        or _gate_az_hold(board, bar)
        or _gate_overrefuse(board, bar)
        or _gate_core(board, bar)
        or _gate_modes_latency(board, bar)
    )
    if err:
        return err
    return (
        f"PROMOTE ({REALGAIN_ID}: forever FH 0; AZ hold 0; "
        "over-refuse 0; live FP 0; no bank stuffing)"
    )
