"""Wave AW1 H-PRODKEEP: hold Caminho A under pressure-para ≠ AV/AU."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aw_session_ops import (
    AW0_ANTI_FP,
    AW0_MODES,
    AW0_PRESSURE_PARA_ROWS,
    AW0_PRODUCT_KEEP_CHARTER,
    AW0_SAFE_NOTE,
    AW0_SHIP_LOCK,
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
    "PRODKEEP_ID",
    "PRODKEEP_THESIS",
    "PRODKEEP_CLAIM",
    "PRODKEEP_SAFE_NOTE",
    "PRODKEEP_ANTI_FP",
    "PRESSURE_PARA_ROWS",
    "NEAR_MISS_ASK",
    "PEAK_ASK",
    "KNOWN_ASK",
    "DECODE_PROBE_ASK",
    "bars_from_keep_charter",
    "human_para_hit",
    "near_miss_ok",
    "peak_ok",
    "decode_content_honest",
    "gate_junk_decode",
    "extract_prodkeep_board",
    "decide_prodkeep",
]

PRODKEEP_ID = "H-PRODKEEP"
PRODKEEP_THESIS = (
    "Hold Caminho A under pressure-para ≠ AV/AU: para ≥ bar; FH 0; "
    "DECODE usable or ABSTAIN; publish para · FH · p50/p99 · KB · modes 4/4; "
    "regression_hold vs AV PRODSHIP/SHIPUI2"
)
PRODKEEP_CLAIM = AW0_SHIP_LOCK
PRODKEEP_SAFE_NOTE = AW0_SAFE_NOTE
PRODKEEP_ANTI_FP = AW0_ANTI_FP
PRESSURE_PARA_ROWS = AW0_PRESSURE_PARA_ROWS


def bars_from_keep_charter(
    suite: Mapping[str, object] | None = None,
) -> dict[str, Any]:
    """
    GIVEN AW0 product-keep charter
    WHEN reading bars
    THEN return typed bar dict for PRODKEEP gate.
    """
    src = suite if suite is not None else AW0_PRODUCT_KEEP_CHARTER
    bars = src.get("bars")
    return dict(bars) if isinstance(bars, dict) else {}


def extract_prodkeep_board(
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
    GIVEN live keep measurements + metrics/ship summaries
    WHEN building PRODKEEP board
    THEN publish pressure-para · FH · DECODE content · latency · KB · modes.
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
    modes = sorted(str(k) for k in paths.keys() if str(k) in AW0_MODES)
    if len(modes) < 4:
        arms = list(ship.get("arms") or [])
        modes = sorted(
            {
                str(a.get("product_mode") or "")
                for a in arms
                if str(a.get("product_mode") or "") in AW0_MODES
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
        "regression_hold": True,
    }


def decide_prodkeep(
    *,
    board: Mapping[str, Any],
    bars: Mapping[str, Any] | None = None,
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN PRODKEEP metrics board
    WHEN applying pesquisa §2 AW1
    THEN PROMOTE iff keep bars hold; else KILL/HOLD.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    bar = bars if bars is not None else bars_from_keep_charter()
    if not bool(bar.get("regression_hold", True)):
        return "KILL (product-keep must require regression_hold)"
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
        return f"HOLD (pressure_para_hit {para:.2f} < {para_min})"
    min_n = int(bar.get("pressure_para_min_n", 20))
    if int(board.get("para_n") or 0) < min_n:
        return f"KILL (pressure para n {board.get('para_n')} < {min_n})"
    modes_req = set(bar.get("modes_required") or list(AW0_MODES))
    modes = set(board.get("modes_visible") or [])
    if modes_req and modes != modes_req:
        return f"KILL (modes visible {sorted(modes)} ≠ {sorted(modes_req)})"
    if not board.get("latency"):
        return "KILL (latency p50/p99 not published)"
    if board.get("kb_coverage_pct") is None:
        return "KILL (KB coverage not published)"
    if not bool(bar.get("decode_gibberish_neq_content_ok", True)):
        return "KILL (DECODE gibberish≠content_ok bar missing)"
    return f"PROMOTE ({PRODKEEP_ID}: Caminho A keep bars held under pressure)"
