"""Wave AV1 H-PRODSHIP: ship Caminho A; close DECODE content debt."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from abstain_ops import apply_abstain, is_junk_decode
from av_session_ops import (
    AV0_ANTI_FP,
    AV0_EXTERNAL_PARA_ROWS,
    AV0_MODES,
    AV0_PRODUCT_SHIP_CHARTER,
    AV0_SAFE_NOTE,
    AV0_SHIP_LOCK,
    map_av_product_mode,
)
from prodhard_ops import (
    KNOWN_ASK,
    NEAR_MISS_ASK,
    PEAK_ASK,
    human_para_hit,
    near_miss_ok,
    peak_ok,
)
from shipreal_ops import attach_shipreal, content_matches_mode

__all__ = [
    "PRODSHIP_ID",
    "PRODSHIP_THESIS",
    "PRODSHIP_CLAIM",
    "PRODSHIP_SAFE_NOTE",
    "PRODSHIP_ANTI_FP",
    "EXTERNAL_PARA_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "bars_from_ship_charter",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "decode_content_honest",
    "gate_junk_decode",
    "extract_prodship_board",
    "decide_prodship",
]

PRODSHIP_ID = "H-PRODSHIP"
PRODSHIP_THESIS = (
    "Ship Caminho A on production ask: external human para ≥ bar; "
    "FH 0; DECODE gibberish ≠ content_ok (usable or ABSTAIN); "
    "publish para · FH · p50/p99 · KB · modes 4/4"
)
PRODSHIP_CLAIM = AV0_SHIP_LOCK
PRODSHIP_SAFE_NOTE = AV0_SAFE_NOTE
PRODSHIP_ANTI_FP = AV0_ANTI_FP
EXTERNAL_PARA_ROWS = AV0_EXTERNAL_PARA_ROWS
DECODE_PROBE_ASK = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)


def bars_from_ship_charter(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AV0 product-ship charter
    WHEN reading bars
    THEN return typed bar dict for PRODSHIP gate.
    """
    src = suite if suite is not None else AV0_PRODUCT_SHIP_CHARTER
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def gate_junk_decode(payload: Mapping[str, Any]) -> dict[str, Any]:
    """
    GIVEN DECODE (or raw wrap-miss) payload
    WHEN junk/gibberish completion
    THEN refuse to ABSTAIN (closes telemetry-only content_ok debt).
    """
    row = dict(payload)
    mode = str(row.get("product_mode") or "")
    if not mode:
        mode = map_av_product_mode(str(row.get("mode") or ""))
        row["product_mode"] = mode
    text = str(row.get("completion", ""))
    if mode in {"DECODE", "UNKNOWN"} or "DECODE" in str(row.get("mode") or "").upper():
        if is_junk_decode(text) and text.strip() != "NO_ANSWER":
            return apply_abstain(row)
    return row


def decode_content_honest(payload: Mapping[str, Any]) -> bool:
    """
    GIVEN DECODE probe row (post gate)
    WHEN applying AV1 DECODE content law
    THEN True iff usable DECODE content_ok OR honest ABSTAIN on junk.
    """
    row = attach_shipreal(dict(payload))
    mode = str(row.get("product_mode") or "")
    if not mode:
        mode = map_av_product_mode(str(row.get("mode") or ""))
        row["product_mode"] = mode
        row = attach_shipreal(row)
    text = str(row.get("completion", "")).strip()
    # Still-showing gibberish as DECODE answer = debt open.
    if mode == "DECODE" and is_junk_decode(text):
        return False
    if mode == "DECODE":
        return content_matches_mode(row)
    if mode == "ABSTAIN" and text == "NO_ANSWER":
        return True
    return False


def extract_prodship_board(
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
    GIVEN live ship measurements + metrics/ship summaries
    WHEN building PRODSHIP board
    THEN publish para · FH · DECODE content · latency · KB · modes.
    """
    n = len(para_hits)
    n_true = int(sum(1 for h in para_hits if h))
    para_hit = float(n_true / n) if n else 0.0
    nm_ok = near_miss_ok(near)
    pk_ok = peak_ok(peak)
    known_ok = human_para_hit(known)
    dec_ok = decode_content_honest(decode)
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
    # Prefer metrics path registry (honest 4/4 publish) over live arms.
    modes = sorted(str(k) for k in paths.keys() if str(k) in AV0_MODES)
    if len(modes) < 4:
        arms = list(ship.get("arms") or [])
        modes = sorted(
            {
                str(a.get("product_mode") or "")
                for a in arms
                if str(a.get("product_mode") or "") in AV0_MODES
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
        "decode_content_ok": dec_ok,
        "decode_mode": decode.get("product_mode") or decode.get("mode"),
        "decode_completion": str(decode.get("completion", ""))[:160],
        "decode_abstained": bool(decode.get("abstained")),
        "latency": latency,
        "kb_coverage_pct": snap.get("coverage_pct"),
        "kb_hole_list": holes,
        "modes_visible": modes,
        "modes_n": len(modes),
    }


def decide_prodship(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN PRODSHIP metrics board
    WHEN applying pesquisa §5 AV1
    THEN PROMOTE iff ship bars hold; else KILL/HOLD.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_ship_charter()
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
    para_min = float(bar.get("para_hit_min", 0.70))
    para = float(board.get("para_hit") or 0.0)
    if para < para_min:
        return f"HOLD (para_hit {para:.2f} < {para_min})"
    min_n = int(bar.get("external_para_min_n", 20))
    if int(board.get("para_n") or 0) < min_n:
        return f"KILL (external para n {board.get('para_n')} < {min_n})"
    modes_req = set(bar.get("modes_required") or list(AV0_MODES))
    modes = set(board.get("modes_visible") or [])
    if modes_req and modes != modes_req:
        return f"KILL (modes visible {sorted(modes)} ≠ {sorted(modes_req)})"
    if not board.get("latency"):
        return "KILL (latency p50/p99 not published)"
    if board.get("kb_coverage_pct") is None:
        return "KILL (KB coverage not published)"
    if not bool(bar.get("decode_gibberish_neq_content_ok", True)):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    return f"PROMOTE ({PRODSHIP_ID}: Caminho A ship bars closed)"
