"""Wave BA3 H-CTXREAL2: usable long/cite/howto content · no anti-FP regress."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from as_dual_hitl_ops import APP_SMOKE_PACK
from ba_session_ops import (
    BA0_ANTI_FP,
    BA0_CTX_BASELINE,
    BA0_MODES,
    BA0_SAFE_NOTE,
    BA0_SHIP_LOCK,
    BA0_SPEED_BASELINE,
)
from prodgen_ops import overrefuse_miss, overrefuse_row_ok
from prodhard_ops import KNOWN_ASK, PEAK_ASK, peak_span_usable
from prodint_ops import intent_false_hit, intent_row_ok
from realgain_ops import AZ_HELDOUT_ROWS, FOREVER_ROWS, OVERREFUSE_ROWS

__all__ = [
    "BA_CTXREAL2_ID",
    "BA_CTXREAL2_THESIS",
    "BA_CTXREAL2_CLAIM",
    "BA_CTXREAL2_SAFE_NOTE",
    "BA_CTXREAL2_ANTI_FP",
    "BA_CTXREAL2_CTX_BASELINE",
    "BA_CTXREAL2_SPEED_BASELINE",
    "CTX_CONTENT_ROWS",
    "APP_SMOKE_PACK",
    "FOREVER_ROWS",
    "AZ_HELDOUT_ROWS",
    "OVERREFUSE_ROWS",
    "KNOWN_ASK",
    "PEAK_ASK",
    "intent_false_hit",
    "intent_row_ok",
    "overrefuse_miss",
    "overrefuse_row_ok",
    "ctx_row_content_ok",
    "apps_ctx_content_ok",
    "extract_ba_ctxreal2_board",
    "decide_ba_ctxreal2",
]

# Lab-book hyp id; AG Wave H-CTXREAL archive stays untouched.
BA_CTXREAL2_ID = "H-CTXREAL2"
BA_CTXREAL2_THESIS = (
    "Publish usable long/cite/howto context content bars on prod path; "
    "PROMOTE only if content_ok on frozen pack + apps smoke, §1 anti-FP holds "
    "(forever FH 0 · AZ hold · over-refuse 0 · live FP 0), p50/p99 published, "
    "modes 4/4 — L_eff alone ≠ win; ≠ AG H-CTXREAL quad-doc L_eff archive"
)
BA_CTXREAL2_CLAIM = BA0_SHIP_LOCK
BA_CTXREAL2_SAFE_NOTE = BA0_SAFE_NOTE
BA_CTXREAL2_ANTI_FP = BA0_ANTI_FP
BA_CTXREAL2_CTX_BASELINE = BA0_CTX_BASELINE
BA_CTXREAL2_SPEED_BASELINE = BA0_SPEED_BASELINE

# Frozen BA context content pack (howto · cite · long) — not L_eff theater.
CTX_CONTENT_ROWS: tuple[dict[str, str], ...] = (
    {
        "id": "BA-CTX-HOWTO-01",
        "kind": "howto",
        "expect_mode": "LOOKUP",
        "question": "Add item `x` to the end of list `a` — one method call.",
        "gold": "a.append(x)",
    },
    {
        "id": "BA-CTX-HOWTO-02",
        "kind": "howto",
        "expect_mode": "LOOKUP",
        "question": str(OVERREFUSE_ROWS[0]["question"]),
        "gold": "a.clear()",
    },
    {
        "id": "BA-CTX-CITE-01",
        "kind": "cite",
        "expect_mode": "LOOKUP",
        "question": (
            "BIP-39: what is the formula for checksum length CS "
            "in terms of ENT? (write CS = …)"
        ),
        "gold": "CS = ENT / 32",
    },
    {
        "id": "BA-CTX-CITE-02",
        "kind": "cite",
        "expect_mode": "LOOKUP",
        "question": KNOWN_ASK,
        "gold": "def add",
    },
    {
        "id": "BA-CTX-LONG-01",
        "kind": "long",
        "expect_mode": "PEAK",
        "question": PEAK_ASK,
        "gold": "Ownership",
    },
)


def _lookup_gold_ok(row: Mapping[str, Any]) -> bool:
    text = str(row.get("completion") or "").strip()
    gold = str(row.get("gold") or "").strip()
    if not text or text == "NO_ANSWER":
        return False
    if gold and gold.lower() not in text.lower():
        return False
    return True


def ctx_row_content_ok(row: Mapping[str, Any]) -> bool:
    """
    GIVEN a BA CTX content row (howto|cite|long)
    WHEN checking usable grounded content
    THEN True iff labeled mode matches kind + gold/span bar.
    """
    kind = str(row.get("kind") or "")
    mode = str(row.get("product_mode") or "")
    text = str(row.get("completion") or "")
    if kind in {"howto", "cite"}:
        if mode != "LOOKUP":
            return False
        return _lookup_gold_ok(row)
    if kind == "long":
        if mode != "PEAK":
            return False
        return peak_span_usable(text)
    return False


def apps_ctx_content_ok(apps: Sequence[Mapping[str, Any]]) -> bool:
    """
    GIVEN apps known-ask · howto · long-doc smoke
    WHEN applying BA3 content bars
    THEN True iff each surface LOOKUP with usable gold content.
    """
    if len(apps) < 3:
        return False
    for row in apps:
        mode = str(row.get("product_mode") or "")
        if mode != "LOOKUP":
            return False
        if not _lookup_gold_ok(row):
            return False
    return True


def extract_ba_ctxreal2_board(
    *,
    ctx_rows: Sequence[Mapping[str, Any]],
    apps_rows: Sequence[Mapping[str, Any]],
    forever_rows: Sequence[Mapping[str, Any]],
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
    GIVEN ctx content + apps + anti-FP + latency
    WHEN building BA3 CTXREAL2 board
    THEN publish content_ok · antifp · p50/p99 · L_eff flag.
    """
    n_ctx = len(ctx_rows)
    n_ctx_ok = int(sum(1 for r in ctx_rows if ctx_row_content_ok(r)))
    n_f = len(forever_rows)
    n_f_fh = int(sum(1 for r in forever_rows if intent_false_hit(r)))
    n_f_ok = int(sum(1 for r in forever_rows if intent_row_ok(r)))
    n_a = len(az_rows)
    n_a_fh = int(sum(1 for r in az_rows if intent_false_hit(r)))
    n_a_ok = int(sum(1 for r in az_rows if intent_row_ok(r)))
    n_o = len(overrefuse_rows)
    n_o_miss = int(sum(1 for r in overrefuse_rows if overrefuse_miss(r)))
    n_o_ok = int(sum(1 for r in overrefuse_rows if overrefuse_row_ok(r)))
    return {
        "ctx_content_ok_n": n_ctx_ok,
        "ctx_content_n": n_ctx,
        "ctx_content_ok": n_ctx_ok == n_ctx and n_ctx >= 5,
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
        "apps_content_ok": apps_ctx_content_ok(apps_rows),
        "apps_n": len(apps_rows),
        "forever_false_hit": n_f_fh,
        "forever_ok_n": n_f_ok,
        "forever_n": n_f,
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
            BA_CTXREAL2_CTX_BASELINE.get("l_eff_alone_insufficient")
        ),
        "content_bars_required": bool(
            BA_CTXREAL2_CTX_BASELINE.get("content_bars_required")
        ),
        "bank_stuff_forbidden": True,
        "ag_ctxreal_archive_untouched": True,
        "baseline_source": str(BA_CTXREAL2_CTX_BASELINE.get("source", "")),
    }


def _gate_forever(board: Mapping[str, Any]) -> str | None:
    if int(board.get("forever_false_hit") or 0) > 0:
        return (
            f"KILL (forever_false_hit {board.get('forever_false_hit')} > 0)"
        )
    if int(board.get("forever_n") or 0) < 15:
        return f"KILL (forever n {board.get('forever_n')} < 15)"
    if int(board.get("forever_ok_n") or 0) < int(board.get("forever_n") or 0):
        return (
            f"HOLD (forever ABSTAIN {board.get('forever_ok_n')}/"
            f"{board.get('forever_n')} incomplete)"
        )
    return None


def _gate_az_orf(board: Mapping[str, Any]) -> str | None:
    if int(board.get("az_hold_false_hit") or 0) > 0:
        return f"KILL (az_hold_false_hit {board.get('az_hold_false_hit')} > 0)"
    if int(board.get("az_hold_n") or 0) < 12:
        return f"KILL (az hold n {board.get('az_hold_n')} < 12)"
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


def _gate_ctx(board: Mapping[str, Any]) -> str | None:
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
    if not bool(board.get("l_eff_alone_insufficient")):
        return "KILL (L_eff alone must stay insufficient)"
    if not bool(board.get("content_bars_required")):
        return "KILL (content bars must stay required)"
    if not bool(board.get("ag_ctxreal_archive_untouched")):
        return "KILL (AG H-CTXREAL archive must stay untouched)"
    return None


def _gate_latency(board: Mapping[str, Any]) -> str | None:
    latency = board.get("latency")
    if not isinstance(latency, dict) or set(latency) != BA0_MODES:
        return "KILL (latency paths incomplete — need LOOKUP·PEAK·DECODE·ABSTAIN)"
    tel = dict(board.get("telemetry_ok") or {})
    for name in BA0_MODES:
        if not bool(tel.get(name)):
            return f"KILL (telemetry_ok failed for {name})"
        row = dict(latency.get(name) or {})
        if row.get("p50_wall_ms") is None or row.get("p99_wall_ms") is None:
            return f"KILL (missing p50/p99 for {name})"
    modes = set(board.get("modes_visible") or [])
    if modes != BA0_MODES:
        return f"KILL (modes visible {sorted(modes)} ≠ charter)"
    return None


def decide_ba_ctxreal2(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN BA3 CTXREAL2 board
    WHEN applying pesquisa §2 + §8 BA3
    THEN PROMOTE iff content bars + anti-FP + latency + modes.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    err = (
        _gate_forever(board)
        or _gate_az_orf(board)
        or _gate_core(board)
        or _gate_ctx(board)
        or _gate_latency(board)
    )
    if err:
        return err
    return (
        f"PROMOTE ({BA_CTXREAL2_ID}: howto·cite·long content_ok; "
        "anti-FP hold; p50/p99 published; L_eff alone ≠ win)"
    )
