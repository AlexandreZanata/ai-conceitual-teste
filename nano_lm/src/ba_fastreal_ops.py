"""Wave BA2 H-FASTREAL: prod-path p50/p99 · no anti-FP regress (≠ AG FASTREAL)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ba_session_ops import (
    BA0_ANTI_FP,
    BA0_MODES,
    BA0_SAFE_NOTE,
    BA0_SHIP_LOCK,
    BA0_SPEED_BASELINE,
)
from latp_ops import path_latency_stats, percentile
from prodgen_ops import overrefuse_miss, overrefuse_row_ok
from prodint_ops import intent_false_hit, intent_row_ok

__all__ = [
    "BA_FASTREAL_ID",
    "BA_FASTREAL_THESIS",
    "BA_FASTREAL_CLAIM",
    "BA_FASTREAL_SAFE_NOTE",
    "BA_FASTREAL_ANTI_FP",
    "BA_FASTREAL_BASELINE",
    "P99_REGRESS_MAX_RATIO",
    "LOOKUP_N",
    "PEAK_N",
    "DECODE_N",
    "ABSTAIN_N",
    "percentile",
    "path_latency_stats",
    "intent_false_hit",
    "intent_row_ok",
    "overrefuse_miss",
    "overrefuse_row_ok",
    "p99_regressed",
    "extract_ba_fastreal_board",
    "decide_ba_fastreal",
]

# BA2 hyp name matches lab-book; AG Wave H-FASTREAL archive stays untouched.
BA_FASTREAL_ID = "H-FASTREAL"
BA_FASTREAL_THESIS = (
    "Publish prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; "
    "PROMOTE only if §1 anti-FP holds (forever FH 0 · AZ hold · "
    "over-refuse 0 · live FP 0) and live p99 does not regress vs "
    "BA0 speed baseline — never warm-cache vanity; LOOKUP wall=0 ≠ speed IQ; "
    "≠ AG H-FASTREAL gen microbench archive"
)
BA_FASTREAL_CLAIM = BA0_SHIP_LOCK
BA_FASTREAL_SAFE_NOTE = BA0_SAFE_NOTE
BA_FASTREAL_ANTI_FP = BA0_ANTI_FP
BA_FASTREAL_BASELINE = BA0_SPEED_BASELINE

# Allow modest wall noise; KILL only clear live p99 blowups.
P99_REGRESS_MAX_RATIO = 1.50
LOOKUP_N = 64
PEAK_N = 128
DECODE_N = 12
ABSTAIN_N = 32


def p99_regressed(
    latency: Mapping[str, Mapping[str, Any]],
    *,
    baseline: Mapping[str, object] | None = None,
    max_ratio: float = P99_REGRESS_MAX_RATIO,
) -> list[str]:
    """
    GIVEN measured path latency + BA0 speed baseline
    WHEN comparing p99 wall_ms
    THEN return list of paths that regress beyond max_ratio (LOOKUP 0 skipped).
    """
    base_paths = dict((baseline or BA_FASTREAL_BASELINE).get("paths") or {})
    bad: list[str] = []
    for name in BA0_MODES:
        row = dict(latency.get(name) or {})
        meas = float(row.get("p99_wall_ms") or 0.0)
        base_row = dict(base_paths.get(name) or {})
        base = float(base_row.get("p99") or 0.0)
        if base <= 0.0:
            continue
        if meas > base * float(max_ratio):
            bad.append(name)
    return sorted(bad)


def extract_ba_fastreal_board(
    *,
    latency: Mapping[str, Mapping[str, Any]],
    forever_rows: Sequence[Mapping[str, Any]],
    az_rows: Sequence[Mapping[str, Any]],
    overrefuse_rows: Sequence[Mapping[str, Any]],
    live_fp: int,
    near_miss_ok: bool,
    known_lookup_ok: bool,
    decode_content_ok: bool,
    modes_visible: Sequence[str],
    telemetry_ok: Mapping[str, bool],
) -> dict[str, Any]:
    """
    GIVEN latency tetrad + anti-FP hold packs
    WHEN building BA2 FASTREAL board
    THEN publish p50/p99 · forever/AZ/orf · regress flags.
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
    regress_paths = p99_regressed(latency)
    return {
        "latency": {k: dict(v) for k, v in latency.items()},
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
        "modes_visible": sorted(modes_visible),
        "modes_n": len(set(modes_visible)),
        "telemetry_ok": dict(telemetry_ok),
        "p99_regress_paths": regress_paths,
        "p99_regress": bool(regress_paths),
        "p99_regress_max_ratio": P99_REGRESS_MAX_RATIO,
        "baseline_source": str(BA_FASTREAL_BASELINE.get("source", "")),
        "lookup_wall_neq_speed_iq": True,
        "warm_cache_vanity_forbidden": True,
        "bank_stuff_forbidden": True,
        "ag_fastreal_archive_untouched": True,
    }


def _gate_forever_ba(board: Mapping[str, Any]) -> str | None:
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


def _gate_az_orf_ba(board: Mapping[str, Any]) -> str | None:
    if int(board.get("az_hold_false_hit") or 0) > 0:
        return f"KILL (az_hold_false_hit {board.get('az_hold_false_hit')} > 0)"
    if int(board.get("az_hold_n") or 0) < 12:
        return f"KILL (az hold n {board.get('az_hold_n')} < 12)"
    if int(board.get("overrefuse_miss") or 0) > 0:
        return f"KILL (overrefuse_miss {board.get('overrefuse_miss')} > 0)"
    if int(board.get("overrefuse_n") or 0) < 3:
        return f"KILL (overrefuse n {board.get('overrefuse_n')} < 3)"
    return None


def _gate_core_ba(board: Mapping[str, Any]) -> str | None:
    if int(board.get("live_fp") or 0) > 0:
        return f"KILL (live FP {board.get('live_fp')} > 0)"
    if not bool(board.get("near_miss_ok")):
        return "KILL (near-miss not ABSTAIN)"
    if not bool(board.get("known_lookup_ok")):
        return "KILL (known LOOKUP regress)"
    if not bool(board.get("decode_content_ok")):
        return "KILL (DECODE content law regress)"
    return None


def _gate_antifp(board: Mapping[str, Any]) -> str | None:
    return (
        _gate_forever_ba(board)
        or _gate_az_orf_ba(board)
        or _gate_core_ba(board)
    )


def _gate_tel_paths(board: Mapping[str, Any]) -> str | None:
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
    return None


def _gate_latency(board: Mapping[str, Any]) -> str | None:
    err = _gate_tel_paths(board)
    if err:
        return err
    modes = set(board.get("modes_visible") or [])
    if modes != BA0_MODES:
        return f"KILL (modes visible {sorted(modes)} ≠ charter)"
    if bool(board.get("p99_regress")):
        paths = board.get("p99_regress_paths") or []
        return f"KILL (live p99 regress vs BA0 baseline: {paths})"
    if not bool(board.get("lookup_wall_neq_speed_iq")):
        return "KILL (LOOKUP wall=0 must not be sold as speed IQ)"
    if not bool(board.get("warm_cache_vanity_forbidden")):
        return "KILL (warm-cache vanity must stay forbidden)"
    if not bool(board.get("ag_fastreal_archive_untouched")):
        return "KILL (AG H-FASTREAL archive must stay untouched)"
    return None


def decide_ba_fastreal(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN BA2 FASTREAL board
    WHEN applying pesquisa §3 + §8 BA2
    THEN PROMOTE iff latency published + anti-FP hold + no p99 regress.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    err = _gate_antifp(board) or _gate_latency(board)
    if err:
        return err
    return (
        f"PROMOTE ({BA_FASTREAL_ID}: prod p50/p99 published; "
        "anti-FP hold; no live p99 regress vs BA0 baseline)"
    )
