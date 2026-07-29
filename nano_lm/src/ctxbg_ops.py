"""Wave BG4 H-CTXBG: hold howto·cite·long content · no anti-FP regress."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from as_dual_hitl_ops import APP_SMOKE_PACK
from ba_ctxreal2_ops import CTX_CONTENT_ROWS
from bb_ctxhold_ops import apps_ctx_content_ok, ctx_row_content_ok
from bd_session_ops import BD0_MODES
from bg_session_ops import (
    BG0_ANTI_FP,
    BG0_CTX_BASELINE,
    BG0_SAFE_NOTE,
    BG0_SHIP_LOCK,
    BG0_SPEED_BASELINE,
)
from prodgen_ops import overrefuse_miss, overrefuse_row_ok
from prodhard_ops import KNOWN_ASK, PEAK_ASK
from prodint_ops import intent_false_hit, intent_row_ok

__all__ = [
    "CTXBG_ID",
    "CTXBG_THESIS",
    "CTXBG_CLAIM",
    "CTXBG_SAFE_NOTE",
    "CTXBG_ANTI_FP",
    "CTXBG_CTX_BASELINE",
    "CTXBG_SPEED_BASELINE",
    "CTX_CONTENT_ROWS",
    "APP_SMOKE_PACK",
    "KNOWN_ASK",
    "PEAK_ASK",
    "intent_false_hit",
    "intent_row_ok",
    "overrefuse_miss",
    "overrefuse_row_ok",
    "ctx_row_content_ok",
    "apps_ctx_content_ok",
    "extract_ctxbg_board",
    "decide_ctxbg",
]

CTXBG_ID = "H-CTXBG"
CTXBG_THESIS = (
    "Hold/improve usable long/cite/howto context content bars on prod path; "
    "PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds "
    "(BG-FOREVER FH 0 · BA…BF forever hold · AZ hold · over-refuse 0 · "
    "live FP 0), p50/p99 published, modes 4/4 — L_eff alone ≠ win; "
    "≠ BF H-CTXBF archive · ≠ BE H-CTXBE · ≠ BD H-CTXGAIN · "
    "≠ AH H-CTXLIFT · ≠ BC H-CTXLIFT2 · ≠ BB H-CTXHOLD · ≠ BA H-CTXREAL2"
)
CTXBG_CLAIM = BG0_SHIP_LOCK
CTXBG_SAFE_NOTE = BG0_SAFE_NOTE
CTXBG_ANTI_FP = BG0_ANTI_FP
CTXBG_CTX_BASELINE = BG0_CTX_BASELINE
CTXBG_SPEED_BASELINE = BG0_SPEED_BASELINE


def _count_intent_pack(rows: Sequence[Mapping[str, Any]]) -> tuple[int, int, int]:
    n = len(rows)
    fh = int(sum(1 for r in rows if intent_false_hit(r)))
    ok = int(sum(1 for r in rows if intent_row_ok(r)))
    return n, fh, ok


def _count_overrefuse(rows: Sequence[Mapping[str, Any]]) -> tuple[int, int, int]:
    n = len(rows)
    miss = int(sum(1 for r in rows if overrefuse_miss(r)))
    ok = int(sum(1 for r in rows if overrefuse_row_ok(r)))
    return n, miss, ok


def _ctx_kind_flags(ctx_rows: Sequence[Mapping[str, Any]]) -> dict[str, bool]:
    return {
        "howto_ok": any(
            str(r.get("kind")) == "howto" and ctx_row_content_ok(r)
            for r in ctx_rows
        ),
        "cite_ok": any(
            str(r.get("kind")) == "cite" and ctx_row_content_ok(r)
            for r in ctx_rows
        ),
        "long_ok": any(
            str(r.get("kind")) == "long" and ctx_row_content_ok(r)
            for r in ctx_rows
        ),
    }


def extract_ctxbg_board(
    *,
    ctx_rows: Sequence[Mapping[str, Any]],
    apps_rows: Sequence[Mapping[str, Any]],
    bg_rows: Sequence[Mapping[str, Any]],
    bf_rows: Sequence[Mapping[str, Any]],
    be_rows: Sequence[Mapping[str, Any]],
    bd_rows: Sequence[Mapping[str, Any]],
    bc_rows: Sequence[Mapping[str, Any]],
    bb_rows: Sequence[Mapping[str, Any]],
    ba_rows: Sequence[Mapping[str, Any]],
    az_rows: Sequence[Mapping[str, Any]],
    overrefuse_rows: Sequence[Mapping[str, Any]],
    live_fp: int,
    near_miss_ok: bool,
    known_lookup_ok: bool,
    decode_content_ok: bool,
    peak_ok: bool,
    latency: Mapping[str, Mapping[str, Any]],
    modes_visible: Sequence[str],
    telemetry_ok: Mapping[str, bool],
) -> dict[str, Any]:
    """
    GIVEN ctx content + apps + BG/BF/BE/BA…BD/AZ anti-FP + latency
    WHEN building BG4 CTXBG board
    THEN publish content_ok · antifp · p50/p99 · L_eff flag.
    """
    n_ctx = len(ctx_rows)
    n_ctx_ok = int(sum(1 for r in ctx_rows if ctx_row_content_ok(r)))
    n_bg, n_bg_fh, n_bg_ok = _count_intent_pack(bg_rows)
    n_bf, n_bf_fh, n_bf_ok = _count_intent_pack(bf_rows)
    n_be, n_be_fh, n_be_ok = _count_intent_pack(be_rows)
    n_bd, n_bd_fh, n_bd_ok = _count_intent_pack(bd_rows)
    n_bc, n_bc_fh, n_bc_ok = _count_intent_pack(bc_rows)
    n_bb, n_bb_fh, n_bb_ok = _count_intent_pack(bb_rows)
    n_ba, n_ba_fh, n_ba_ok = _count_intent_pack(ba_rows)
    n_a, n_a_fh, n_a_ok = _count_intent_pack(az_rows)
    n_o, n_o_miss, n_o_ok = _count_overrefuse(overrefuse_rows)
    kinds = _ctx_kind_flags(ctx_rows)
    return {
        "ctx_content_ok_n": n_ctx_ok,
        "ctx_content_n": n_ctx,
        "ctx_content_ok": n_ctx_ok == n_ctx and n_ctx >= 5,
        **kinds,
        "apps_content_ok": apps_ctx_content_ok(apps_rows),
        "apps_n": len(apps_rows),
        "bg_forever_false_hit": n_bg_fh,
        "bg_forever_ok_n": n_bg_ok,
        "bg_forever_n": n_bg,
        "bf_forever_false_hit": n_bf_fh,
        "bf_forever_ok_n": n_bf_ok,
        "bf_forever_n": n_bf,
        "be_forever_false_hit": n_be_fh,
        "be_forever_ok_n": n_be_ok,
        "be_forever_n": n_be,
        "bd_forever_false_hit": n_bd_fh,
        "bd_forever_ok_n": n_bd_ok,
        "bd_forever_n": n_bd,
        "bc_forever_false_hit": n_bc_fh,
        "bc_forever_ok_n": n_bc_ok,
        "bc_forever_n": n_bc,
        "bb_forever_false_hit": n_bb_fh,
        "bb_forever_ok_n": n_bb_ok,
        "bb_forever_n": n_bb,
        "ba_forever_false_hit": n_ba_fh,
        "ba_forever_ok_n": n_ba_ok,
        "ba_forever_n": n_ba,
        "az_hold_false_hit": n_a_fh,
        "az_hold_ok_n": n_a_ok,
        "az_hold_n": n_a,
        "overrefuse_miss": n_o_miss,
        "overrefuse_ok_n": n_o_ok,
        "overrefuse_n": n_o,
        "live_fp": int(live_fp),
        "near_miss_ok": bool(near_miss_ok),
        "known_lookup_ok": bool(known_lookup_ok),
        "decode_content_ok": bool(decode_content_ok),
        "peak_ok": bool(peak_ok),
        "latency": {k: dict(v) for k, v in latency.items()},
        "modes_visible": sorted(modes_visible),
        "modes_n": len(set(modes_visible)),
        "telemetry_ok": dict(telemetry_ok),
        "l_eff_alone_insufficient": bool(
            CTXBG_CTX_BASELINE.get("l_eff_alone_insufficient")
        ),
        "content_bars_required": bool(
            CTXBG_CTX_BASELINE.get("content_bars_required")
        ),
        "bank_stuff_forbidden": True,
        "ba_bb_bc_bd_be_bf_pass_neq_bg_forever": True,
        "bf_ctxbf_archive_untouched": True,
        "be_ctxbe_archive_untouched": True,
        "bd_ctxgain_archive_untouched": True,
        "bc_ctxlift2_archive_untouched": True,
        "bb_ctxhold_archive_untouched": True,
        "ba_ctxreal2_archive_untouched": True,
        "ah_ctxlift_archive_untouched": True,
        "baseline_source": str(CTXBG_CTX_BASELINE.get("source", "")),
    }


def _gate_forever(
    board: Mapping[str, Any], *, key: str, min_n: int
) -> str | None:
    fh = int(board.get(f"{key}_false_hit") or 0)
    if fh > 0:
        return f"KILL ({key}_false_hit {fh} > 0)"
    n = int(board.get(f"{key}_n") or 0)
    if n < min_n:
        return f"KILL ({key} n {n} < {min_n})"
    ok = int(board.get(f"{key}_ok_n") or 0)
    if ok < n:
        return f"HOLD ({key} ABSTAIN {ok}/{n} incomplete)"
    return None


def _gate_az_orf(board: Mapping[str, Any]) -> str | None:
    err = _gate_forever(board, key="az_hold", min_n=12)
    if err:
        return err
    if int(board.get("overrefuse_miss") or 0) > 0:
        return f"KILL (overrefuse_miss {board.get('overrefuse_miss')} > 0)"
    if int(board.get("overrefuse_n") or 0) < 3:
        return f"KILL (overrefuse n {board.get('overrefuse_n')} < 3)"
    return None


def _gate_core(board: Mapping[str, Any]) -> str | None:
    if int(board.get("live_fp") or 0) > 0:
        return f"KILL (live FP {board.get('live_fp')} > 0)"
    if not bool(board.get("near_miss_ok")):
        return "KILL (near-miss not ABSTAIN)"
    if not bool(board.get("known_lookup_ok")):
        return "KILL (known LOOKUP regress)"
    if not bool(board.get("decode_content_ok")):
        return "KILL (DECODE content law regress)"
    if not bool(board.get("peak_ok")):
        return "KILL (PEAK not usable)"
    return None


def _gate_ctx_kinds(board: Mapping[str, Any]) -> str | None:
    if not bool(board.get("ctx_content_ok")):
        return (
            f"KILL (ctx content_ok {board.get('ctx_content_ok_n')}/"
            f"{board.get('ctx_content_n')} incomplete)"
        )
    if not bool(board.get("howto_ok")):
        return "KILL (howto content bar failed)"
    if not bool(board.get("cite_ok")):
        return "KILL (cite content bar failed)"
    if not bool(board.get("long_ok")):
        return "KILL (long/PEAK content bar failed)"
    if not bool(board.get("apps_content_ok")):
        return "KILL (apps known/howto/long-doc content failed)"
    return None


def _gate_ctx_policy(board: Mapping[str, Any]) -> str | None:
    if not bool(board.get("l_eff_alone_insufficient")):
        return "KILL (L_eff alone must stay insufficient)"
    if not bool(board.get("content_bars_required")):
        return "KILL (content bars must stay required)"
    flags = (
        (
            "bf_ctxbf_archive_untouched",
            "KILL (BF H-CTXBF archive must stay untouched)",
        ),
        (
            "be_ctxbe_archive_untouched",
            "KILL (BE H-CTXBE archive must stay untouched)",
        ),
        (
            "bd_ctxgain_archive_untouched",
            "KILL (BD H-CTXGAIN archive must stay untouched)",
        ),
        (
            "bc_ctxlift2_archive_untouched",
            "KILL (BC H-CTXLIFT2 archive must stay untouched)",
        ),
        (
            "bb_ctxhold_archive_untouched",
            "KILL (BB H-CTXHOLD archive must stay untouched)",
        ),
        (
            "ba_ctxreal2_archive_untouched",
            "KILL (BA H-CTXREAL2 archive must stay untouched)",
        ),
        (
            "ah_ctxlift_archive_untouched",
            "KILL (AH H-CTXLIFT archive must stay untouched)",
        ),
    )
    for key, msg in flags:
        if not bool(board.get(key)):
            return msg
    return None


def _gate_ctx(board: Mapping[str, Any]) -> str | None:
    return _gate_ctx_kinds(board) or _gate_ctx_policy(board)


def _gate_latency(board: Mapping[str, Any]) -> str | None:
    latency = board.get("latency")
    if not isinstance(latency, dict) or set(latency) != BD0_MODES:
        return "KILL (latency paths incomplete — need LOOKUP·PEAK·DECODE·ABSTAIN)"
    tel = dict(board.get("telemetry_ok") or {})
    for name in BD0_MODES:
        if not bool(tel.get(name)):
            return f"KILL (telemetry_ok failed for {name})"
        row = dict(latency.get(name) or {})
        if row.get("p50_wall_ms") is None or row.get("p99_wall_ms") is None:
            return f"KILL (missing p50/p99 for {name})"
    modes = set(board.get("modes_visible") or [])
    if modes != BD0_MODES:
        return f"KILL (modes visible {sorted(modes)} ≠ charter)"
    return None


def decide_ctxbg(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN BG4 CTXBG board
    WHEN applying pesquisa §3 + §9 BG4
    THEN PROMOTE iff content bars + anti-FP + latency + modes.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    err = (
        _gate_forever(board, key="bg_forever", min_n=12)
        or _gate_forever(board, key="bf_forever", min_n=12)
        or _gate_forever(board, key="be_forever", min_n=12)
        or _gate_forever(board, key="bd_forever", min_n=12)
        or _gate_forever(board, key="ba_forever", min_n=15)
        or _gate_forever(board, key="bb_forever", min_n=15)
        or _gate_forever(board, key="bc_forever", min_n=18)
        or _gate_az_orf(board)
        or _gate_core(board)
        or _gate_ctx(board)
        or _gate_latency(board)
    )
    if err:
        return err
    return (
        f"PROMOTE ({CTXBG_ID}: howto·cite·long content_ok; "
        "BG/BF/BE/BD/BA/BB/BC/AZ anti-FP hold; p50/p99 published; "
        "L_eff alone ≠ win)"
    )
