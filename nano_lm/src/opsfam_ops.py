"""Wave BC1 H-OPSFAM: BC-FOREVER FH 0 · BA/BB/AZ hold · live board."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from az_session_ops import (
    AZ0_HELDOUT_FP_ROWS,
    AZ0_MODES,
    AZ0_OVERREFUSE_ROWS,
)
from ba_session_ops import BA0_FOREVER_ROWS
from bb_session_ops import BB0_FOREVER_ROWS
from bc_session_ops import (
    BC0_ANTI_FP,
    BC0_FOREVER_ROWS,
    BC0_SAFE_NOTE,
    BC0_SCOREBOARD,
    BC0_SHIP_LOCK,
    map_bc_product_mode,
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
    "OPSFAM_ID",
    "OPSFAM_THESIS",
    "OPSFAM_CLAIM",
    "OPSFAM_SAFE_NOTE",
    "OPSFAM_ANTI_FP",
    "BC_FOREVER_ROWS",
    "BA_FOREVER_ROWS",
    "BB_FOREVER_ROWS",
    "AZ_HELDOUT_ROWS",
    "OVERREFUSE_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "NOVEL_PROBES",
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
    "map_bc_product_mode",
    "score_live_row",
    "extract_opsfam_board",
    "decide_opsfam",
]

OPSFAM_ID = "H-OPSFAM"
OPSFAM_THESIS = (
    "Drive BC-FOREVER held-out FH → 0 (floordiv≠add · neg≠add · gcd≠add · "
    "lshift≠add · rshift≠add · nand≠add) via SEMWRAP family ops/intent "
    "gate — not bank stuffing; hold BA-FOREVER + BB-FOREVER + AZ "
    "div·sub·BIP FH 0 + a.clear() LOOKUP; live ask scoreboard "
    "OK|FP|MISS|ABSTAIN-OK (≥10 novel); modes · p50/p99 · DECODE law"
)
OPSFAM_CLAIM = BC0_SHIP_LOCK
OPSFAM_SAFE_NOTE = BC0_SAFE_NOTE
OPSFAM_ANTI_FP = BC0_ANTI_FP
BC_FOREVER_ROWS = BC0_FOREVER_ROWS
BA_FOREVER_ROWS = BA0_FOREVER_ROWS
BB_FOREVER_ROWS = BB0_FOREVER_ROWS
AZ_HELDOUT_ROWS = AZ0_HELDOUT_FP_ROWS
OVERREFUSE_ROWS = AZ0_OVERREFUSE_ROWS

# Novel probes outside exact BA+BB+BC forever seeds (≥10 · anti pack theater).
NOVEL_PROBES: tuple[dict[str, str], ...] = (
    {
        "id": "BC-NOVEL-01",
        "class": "ops_floordiv",
        "expect_mode": "ABSTAIN",
        "question": (
            "Implement floor_div_pair(a,b) returning integer // of a by b "
            "— not a+b."
        ),
    },
    {
        "id": "BC-NOVEL-02",
        "class": "ops_floordiv",
        "expect_mode": "ABSTAIN",
        "question": (
            "I need // for ints as ifloordiv — floor quotient only, never sum."
        ),
    },
    {
        "id": "BC-NOVEL-03",
        "class": "ops_neg",
        "expect_mode": "ABSTAIN",
        "question": (
            "Unary minus helper negate_one(x) returning -x for an int — "
            "not add."
        ),
    },
    {
        "id": "BC-NOVEL-04",
        "class": "ops_neg",
        "expect_mode": "ABSTAIN",
        "question": (
            "Show a tiny function that returns the negation of integer a "
            "only (unary)."
        ),
    },
    {
        "id": "BC-NOVEL-05",
        "class": "ops_gcd",
        "expect_mode": "ABSTAIN",
        "question": (
            "Greatest common divisor helper gcds(a,b) — not their sum."
        ),
    },
    {
        "id": "BC-NOVEL-06",
        "class": "ops_gcd",
        "expect_mode": "ABSTAIN",
        "question": (
            "Please author a gcd helper using math.gcd semantics for a,b "
            "— never a+b."
        ),
    },
    {
        "id": "BC-NOVEL-07",
        "class": "ops_lshift",
        "expect_mode": "ABSTAIN",
        "question": (
            "Bit left-shift helper shift_left(a,b) returning a << b — "
            "not add."
        ),
    },
    {
        "id": "BC-NOVEL-08",
        "class": "ops_rshift",
        "expect_mode": "ABSTAIN",
        "question": (
            "Bit right-shift helper shift_right(a,b) returning a >> b — "
            "not add."
        ),
    },
    {
        "id": "BC-NOVEL-09",
        "class": "ops_nand",
        "expect_mode": "ABSTAIN",
        "question": (
            "Bitwise NAND helper bit_nand(a,b) returning ~(a & b) — "
            "never a+b."
        ),
    },
    {
        "id": "BC-NOVEL-10",
        "class": "ops_nand",
        "expect_mode": "ABSTAIN",
        "question": (
            "I want nand of two ints as not_and_bits — not their sum."
        ),
    },
)


def bars_from_scoreboard(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN BC0 §1 scoreboard
    WHEN reading bars
    THEN return typed bar dict for OPSFAM gate.
    """
    src = suite if suite is not None else BC0_SCOREBOARD
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def score_live_row(row: Mapping[str, Any], *, expect_mode: str) -> str:
    """
    GIVEN live ask result + expected mode
    WHEN scoring OK|FP|MISS|ABSTAIN-OK
    THEN classify per pesquisa §1 anti-FP dictionary.
    """
    mode = str(
        row.get("product_mode") or map_bc_product_mode(str(row.get("mode", "")))
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


def extract_opsfam_board(
    *,
    bc_rows: Sequence[Mapping[str, Any]],
    ba_rows: Sequence[Mapping[str, Any]],
    bb_rows: Sequence[Mapping[str, Any]],
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
    GIVEN BC-FOREVER + BA/BB hold + AZ hold + over-refuse + live scores
    WHEN building OPSFAM board
    THEN publish BC FH · BA/BB hold · AZ hold · over-refuse · live · latency.
    """
    n_bc = len(bc_rows)
    n_bc_fh = int(sum(1 for r in bc_rows if intent_false_hit(r)))
    n_bc_ok = int(sum(1 for r in bc_rows if intent_row_ok(r)))
    n_ba = len(ba_rows)
    n_ba_fh = int(sum(1 for r in ba_rows if intent_false_hit(r)))
    n_ba_ok = int(sum(1 for r in ba_rows if intent_row_ok(r)))
    n_bb = len(bb_rows)
    n_bb_fh = int(sum(1 for r in bb_rows if intent_false_hit(r)))
    n_bb_ok = int(sum(1 for r in bb_rows if intent_row_ok(r)))
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
        "bc_forever_false_hit": n_bc_fh,
        "bc_forever_ok_n": n_bc_ok,
        "bc_forever_n": n_bc,
        "ba_forever_false_hit": n_ba_fh,
        "ba_forever_ok_n": n_ba_ok,
        "ba_forever_n": n_ba,
        "bb_forever_false_hit": n_bb_fh,
        "bb_forever_ok_n": n_bb_ok,
        "bb_forever_n": n_bb,
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
        "ba_bb_pass_neq_bc_forever": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }


def _gate_bc_forever(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    fh_max = int(bar.get("bc_forever_false_hit_max", 0))
    fh = int(board.get("bc_forever_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (bc_forever_false_hit {fh} > {fh_max})"
    min_n = int(bar.get("bc_forever_min_n", 18))
    if int(board.get("bc_forever_n") or 0) < min_n:
        return f"KILL (bc forever n {board.get('bc_forever_n')} < {min_n})"
    if int(board.get("bc_forever_ok_n") or 0) < int(board.get("bc_forever_n") or 0):
        return (
            f"HOLD (bc forever ABSTAIN {board.get('bc_forever_ok_n')}/"
            f"{board.get('bc_forever_n')} incomplete)"
        )
    return None


def _gate_ba_forever(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    fh_max = int(bar.get("ba_forever_false_hit_max", 0))
    fh = int(board.get("ba_forever_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (ba_forever_false_hit {fh} > {fh_max})"
    if int(board.get("ba_forever_n") or 0) < 15:
        return f"KILL (ba forever n {board.get('ba_forever_n')} < 15)"
    if int(board.get("ba_forever_ok_n") or 0) < int(board.get("ba_forever_n") or 0):
        return (
            f"HOLD (ba forever ABSTAIN {board.get('ba_forever_ok_n')}/"
            f"{board.get('ba_forever_n')} incomplete)"
        )
    return None


def _gate_bb_forever(
    board: Mapping[str, Any], bar: Mapping[str, Any]
) -> str | None:
    fh_max = int(bar.get("bb_forever_false_hit_max", 0))
    fh = int(board.get("bb_forever_false_hit") or 0)
    if fh > fh_max:
        return f"KILL (bb_forever_false_hit {fh} > {fh_max})"
    if int(board.get("bb_forever_n") or 0) < 15:
        return f"KILL (bb forever n {board.get('bb_forever_n')} < 15)"
    if int(board.get("bb_forever_ok_n") or 0) < int(board.get("bb_forever_n") or 0):
        return (
            f"HOLD (bb forever ABSTAIN {board.get('bb_forever_ok_n')}/"
            f"{board.get('bb_forever_n')} incomplete)"
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


def _gate_core_flags(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    if not bool(bar.get("bank_stuff_forbidden", True)):
        return "KILL (bank stuffing must stay forbidden)"
    if not bool(bar.get("pack_pass_neq_forever", True)):
        return "KILL (pack PASS ≠ forever bar missing)"
    if not bool(bar.get("ba_bb_pass_neq_bc_forever", True)):
        return "KILL (BA+BB PASS ≠ BC forever bar missing)"
    if not bool(bar.get("regression_hold", True)):
        return "KILL (must require regression_hold)"
    return None


def _gate_core_arms(board: Mapping[str, Any]) -> str | None:
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


def _gate_core(board: Mapping[str, Any], bar: Mapping[str, Any]) -> str | None:
    return _gate_core_flags(board, bar) or _gate_core_arms(board)


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
    novel_min = int(bar.get("novel_probes_min", 10))
    live = dict(board.get("live_scores") or {})
    # live pack includes forever samples + novel; require FP0 already gated
    if sum(int(v) for v in live.values()) < novel_min:
        return f"KILL (live scoreboard rows < novel_probes_min {novel_min})"
    return None


def decide_opsfam(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN OPSFAM metrics board
    WHEN applying pesquisa §9 BC1
    THEN PROMOTE iff BC FH 0 + BA/BB hold 0 + AZ hold 0 + over-refuse 0 + live FP 0.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_scoreboard()
    err = (
        _gate_bc_forever(board, bar)
        or _gate_ba_forever(board, bar)
        or _gate_bb_forever(board, bar)
        or _gate_az_hold(board, bar)
        or _gate_overrefuse(board, bar)
        or _gate_core(board, bar)
        or _gate_modes_latency(board, bar)
    )
    if err:
        return err
    return (
        f"PROMOTE ({OPSFAM_ID}: BC-FOREVER FH 0; BA/BB hold 0; "
        "AZ hold 0; over-refuse 0; live FP 0; no bank stuffing)"
    )
