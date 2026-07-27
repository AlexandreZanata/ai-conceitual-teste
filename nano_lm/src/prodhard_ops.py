"""Wave AU1 H-PRODHARD: close live-audit debts on default ask path."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from au_session_ops import (
    AU0_ANTI_FP,
    AU0_HUMAN_PARA_ROWS,
    AU0_MODES,
    AU0_PRODUCT_DEBT_SUITE,
    AU0_SAFE_NOTE,
    AU0_SHIP_LOCK,
    map_au_product_mode,
)

__all__ = [
    "PRODHARD_ID",
    "PRODHARD_THESIS",
    "PRODHARD_CLAIM",
    "PRODHARD_SAFE_NOTE",
    "PRODHARD_ANTI_FP",
    "HUMAN_PARA_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "bars_from_debt_suite",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "peak_span_usable",
    "extract_prodhard_board",
    "decide_prodhard",
]

PRODHARD_ID = "H-PRODHARD"
PRODHARD_THESIS = (
    "Close live-audit debts on production ask path: near-miss → ABSTAIN; "
    "held-out human para ≥ bar; PEAK usable span or ABSTAIN; publish "
    "para · FH · p50/p99 · KB · modes"
)
PRODHARD_CLAIM = AU0_SHIP_LOCK
PRODHARD_SAFE_NOTE = AU0_SAFE_NOTE
PRODHARD_ANTI_FP = AU0_ANTI_FP
HUMAN_PARA_ROWS = AU0_HUMAN_PARA_ROWS
NEAR_MISS_ASK = (
    "BIP-39 entropy formula is CS = ENT / 32 — confirm for "
    "SegWit witness discount?"
)
PEAK_ASK = (
    "From the curated Rust book intro, extract one sentence on "
    "ownership (label PEAK, not open chat)."
)
KNOWN_ASK = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)


def bars_from_debt_suite(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AU0 product-debt suite
    WHEN reading bars
    THEN return typed bar dict for PRODHARD gate.
    """
    src = suite if suite is not None else AU0_PRODUCT_DEBT_SUITE
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def peak_span_usable(text: str) -> bool:
    """
    GIVEN PEAK completion text
    WHEN checking live-audit usable-span bar
    THEN True iff readable multi-word span (not mid-word fragment).
    """
    t = str(text or "").strip()
    if len(t) < 12:
        return False
    if t == "NO_ANSWER":
        return False
    if set(t) <= {".", " ", "`"}:
        return False
    if t[0].islower() and not t.startswith(("`", "_")):
        return False
    words = [w for w in t.replace(":", " ").split() if w]
    return len(words) >= 3


def human_para_hit(payload: Mapping[str, Any]) -> bool:
    """True iff default-ask LOOKUP recovered def add gold."""
    mode = map_au_product_mode(str(payload.get("mode") or ""))
    if mode != "LOOKUP":
        # also accept product_mode
        mode = str(payload.get("product_mode") or mode)
    if mode != "LOOKUP":
        return False
    return "def add" in str(payload.get("completion", ""))


def near_miss_ok(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN near-miss BIP-39+SegWit ask on default path
    WHEN checking AU1 bar
    THEN must ABSTAIN; LOOKUP of CS=ENT/32 is FALSE_HIT.
    """
    mode = str(payload.get("product_mode") or "")
    if not mode:
        mode = map_au_product_mode(str(payload.get("mode") or ""))
    comp = str(payload.get("completion", "")).lower().replace(" ", "")
    if mode == "LOOKUP" and ("cs=ent/32" in comp or "cs=ent÷32" in comp):
        return False
    return mode == "ABSTAIN"


def peak_ok(payload: Mapping[str, Any]) -> bool:
    """PEAK usable span OR honest ABSTAIN."""
    raw = str(payload.get("mode") or "")
    mode = str(payload.get("product_mode") or "")
    if not mode:
        mode = map_au_product_mode(raw)
    if mode == "ABSTAIN" or raw == "NO_ANSWER":
        return True
    is_peak = mode == "PEAK" or "PEAK" in raw.upper()
    if not is_peak:
        return False
    return peak_span_usable(str(payload.get("completion", "")))


def extract_prodhard_board(
    *,
    para_hits: Sequence[bool],
    near: Mapping[str, Any],
    peak: Mapping[str, Any],
    known: Mapping[str, Any],
    metrics: Mapping[str, Any],
    ship: Mapping[str, Any],
) -> dict[str, Any]:
    """
    GIVEN live debt measurements + metrics/ship summaries
    WHEN building PRODHARD board
    THEN publish para · FH · latency · KB · modes · debt flags.
    """
    n = len(para_hits)
    n_true = int(sum(1 for h in para_hits if h))
    para_hit = float(n_true / n) if n else 0.0
    nm_ok = near_miss_ok(near)
    pk_ok = peak_ok(peak)
    known_ok = human_para_hit(known)
    false_hit = 0 if nm_ok else 1
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
    holes = list(
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
        "para_hit": para_hit,
        "para_n_true": n_true,
        "para_n": n,
        "false_hit": false_hit,
        "near_miss_ok": nm_ok,
        "near_miss_mode": near.get("product_mode") or near.get("mode"),
        "peak_ok": pk_ok,
        "peak_mode": peak.get("product_mode") or peak.get("mode"),
        "peak_completion": str(peak.get("completion", ""))[:160],
        "known_lookup_ok": known_ok,
        "latency": latency,
        "kb_coverage_pct": snap.get("coverage_pct"),
        "kb_hole_list": holes,
        "modes_visible": modes,
        "modes_n": len(modes),
    }


def decide_prodhard(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN PRODHARD metrics board
    WHEN applying pesquisa §5 AU1
    THEN PROMOTE iff live-audit bars hold; else KILL/HOLD.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_debt_suite()
    if not bool(board.get("near_miss_ok")):
        return "KILL (near-miss on default ask not ABSTAIN)"
    fh_max = int(bar.get("false_hit_max", 0))
    fh = int(board.get("false_hit") or 0)
    if fh > fh_max:
        return f"KILL (false_hit {fh} > {fh_max})"
    if not bool(board.get("peak_ok")):
        return "KILL (PEAK not usable and not ABSTAIN)"
    if not bool(board.get("known_lookup_ok")):
        return "KILL (known LOOKUP regress)"
    para_min = float(bar.get("para_hit_min", 0.70))
    para = float(board.get("para_hit") or 0.0)
    if para < para_min:
        return f"HOLD (para_hit {para:.2f} < {para_min})"
    modes_req = set(bar.get("modes_required") or list(AU0_MODES))
    modes = set(board.get("modes_visible") or [])
    if modes_req and modes != modes_req:
        return f"KILL (modes visible {sorted(modes)} ≠ {sorted(modes_req)})"
    if not board.get("latency"):
        return "KILL (latency p50/p99 not published)"
    if board.get("kb_coverage_pct") is None:
        return "KILL (KB coverage not published)"
    return f"PROMOTE ({PRODHARD_ID}: live-audit debts closed)"
