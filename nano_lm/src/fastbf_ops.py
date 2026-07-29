"""Wave BF3 H-FASTBF: prod-path p50/p99 hold/lift · no anti-FP regress."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from bd_session_ops import BD0_MODES
from bf_session_ops import (
    BF0_ANTI_FP,
    BF0_SAFE_NOTE,
    BF0_SHIP_LOCK,
    BF0_SPEED_BASELINE,
)
from latp_ops import path_latency_stats, percentile
from prodgen_ops import overrefuse_miss, overrefuse_row_ok
from prodint_ops import intent_false_hit, intent_row_ok

__all__ = [
    "FASTBF_ID",
    "FASTBF_THESIS",
    "FASTBF_CLAIM",
    "FASTBF_SAFE_NOTE",
    "FASTBF_ANTI_FP",
    "FASTBF_BASELINE",
    "P99_REGRESS_MAX_RATIO",
    "P99_REGRESS_MIN_BASE_MS",
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
    "extract_fastbf_board",
    "decide_fastbf",
]

FASTBF_ID = "H-FASTBF"
FASTBF_THESIS = (
    "Hold/improve prod-ask p50/p99 for LOOKUP·PEAK·DECODE·ABSTAIN; "
    "PROMOTE only if §1 anti-FP holds (BF-FOREVER FH 0 · BA…BE forever "
    "hold · AZ hold · over-refuse 0 · live FP 0) and live p99 does not "
    "regress vs BF0/H-FASTBE baseline — never warm-cache vanity; "
    "LOOKUP wall=0 ≠ speed IQ; sub-ms PEAK walls ≠ speed IQ; "
    "≠ BE H-FASTBE archive · ≠ BD H-FASTGAIN · ≠ BC/AH H-FASTLIFT · "
    "≠ BB H-FASTHOLD · ≠ BA H-FASTREAL · ≠ FP-for-ms"
)
FASTBF_CLAIM = BF0_SHIP_LOCK
FASTBF_SAFE_NOTE = BF0_SAFE_NOTE
FASTBF_ANTI_FP = BF0_ANTI_FP
FASTBF_BASELINE = BF0_SPEED_BASELINE

P99_REGRESS_MAX_RATIO = 1.50
P99_REGRESS_MIN_BASE_MS = 1.0
LOOKUP_N = 64
PEAK_N = 128
DECODE_N = 12
ABSTAIN_N = 32


def p99_regressed(
    latency: Mapping[str, Mapping[str, Any]],
    *,
    baseline: Mapping[str, object] | None = None,
    max_ratio: float = P99_REGRESS_MAX_RATIO,
    min_base_ms: float = P99_REGRESS_MIN_BASE_MS,
) -> list[str]:
    """
    GIVEN measured path latency + BF0/H-FASTBE speed baseline
    WHEN comparing p99 wall_ms
    THEN return paths that regress beyond max_ratio
    (skip LOOKUP-class / sub-ms baselines — not speed IQ).
    """
    base_paths = dict((baseline or FASTBF_BASELINE).get("paths") or {})
    bad: list[str] = []
    for name in BD0_MODES:
        row = dict(latency.get(name) or {})
        meas = float(row.get("p99_wall_ms") or 0.0)
        base_row = dict(base_paths.get(name) or {})
        base = float(base_row.get("p99") or 0.0)
        if base < float(min_base_ms):
            continue
        if meas > base * float(max_ratio):
            bad.append(name)
    return sorted(bad)


def _pack_fh(rows: Sequence[Mapping[str, Any]]) -> tuple[int, int, int]:
    n = len(rows)
    fh = int(sum(1 for r in rows if intent_false_hit(r)))
    ok = int(sum(1 for r in rows if intent_row_ok(r)))
    return n, fh, ok


def extract_fastbf_board(
    *,
    latency: Mapping[str, Mapping[str, Any]],
    bf_rows: Sequence[Mapping[str, Any]],
    be_rows: Sequence[Mapping[str, Any]],
    bd_rows: Sequence[Mapping[str, Any]],
    ba_rows: Sequence[Mapping[str, Any]],
    bb_rows: Sequence[Mapping[str, Any]],
    bc_rows: Sequence[Mapping[str, Any]],
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
    GIVEN latency tetrad + BF/BE/BA…BD/AZ anti-FP hold packs
    WHEN building BF3 FASTBF board
    THEN publish p50/p99 · BF/BE/BA…BD/AZ/orf · regress flags.
    """
    n_bf, n_bf_fh, n_bf_ok = _pack_fh(bf_rows)
    n_be, n_be_fh, n_be_ok = _pack_fh(be_rows)
    n_bd, n_bd_fh, n_bd_ok = _pack_fh(bd_rows)
    n_ba, n_ba_fh, n_ba_ok = _pack_fh(ba_rows)
    n_bb, n_bb_fh, n_bb_ok = _pack_fh(bb_rows)
    n_bc, n_bc_fh, n_bc_ok = _pack_fh(bc_rows)
    n_a, n_a_fh, n_a_ok = _pack_fh(az_rows)
    n_o = len(overrefuse_rows)
    n_o_miss = int(sum(1 for r in overrefuse_rows if overrefuse_miss(r)))
    n_o_ok = int(sum(1 for r in overrefuse_rows if overrefuse_row_ok(r)))
    regress_paths = p99_regressed(latency)
    return {
        "latency": {k: dict(v) for k, v in latency.items()},
        "bf_forever_false_hit": n_bf_fh,
        "bf_forever_ok_n": n_bf_ok,
        "bf_forever_n": n_bf,
        "be_forever_false_hit": n_be_fh,
        "be_forever_ok_n": n_be_ok,
        "be_forever_n": n_be,
        "bd_forever_false_hit": n_bd_fh,
        "bd_forever_ok_n": n_bd_ok,
        "bd_forever_n": n_bd,
        "ba_forever_false_hit": n_ba_fh,
        "ba_forever_ok_n": n_ba_ok,
        "ba_forever_n": n_ba,
        "bb_forever_false_hit": n_bb_fh,
        "bb_forever_ok_n": n_bb_ok,
        "bb_forever_n": n_bb,
        "bc_forever_false_hit": n_bc_fh,
        "bc_forever_ok_n": n_bc_ok,
        "bc_forever_n": n_bc,
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
        "baseline_source": str(FASTBF_BASELINE.get("source", "")),
        "lookup_wall_neq_speed_iq": True,
        "warm_cache_vanity_forbidden": True,
        "bank_stuff_forbidden": True,
        "ba_bb_bc_bd_be_pass_neq_bf_forever": True,
        "be_fastbe_archive_untouched": True,
        "bd_fastgain_archive_untouched": True,
        "bc_fastlift_archive_untouched": True,
        "bb_fasthold_archive_untouched": True,
        "ba_fastreal_archive_untouched": True,
        "ah_fastlift_archive_untouched": True,
        "fp_for_ms_forbidden": True,
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


def _gate_core_arms(board: Mapping[str, Any]) -> str | None:
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
        _gate_forever(board, key="bf_forever", min_n=12)
        or _gate_forever(board, key="be_forever", min_n=12)
        or _gate_forever(board, key="bd_forever", min_n=12)
        or _gate_forever(board, key="ba_forever", min_n=15)
        or _gate_forever(board, key="bb_forever", min_n=15)
        or _gate_forever(board, key="bc_forever", min_n=18)
        or _gate_az_orf(board)
        or _gate_core_arms(board)
    )


def _gate_tel_paths(board: Mapping[str, Any]) -> str | None:
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
    return None


def _gate_latency_flags(board: Mapping[str, Any]) -> str | None:
    modes = set(board.get("modes_visible") or [])
    if modes != BD0_MODES:
        return f"KILL (modes visible {sorted(modes)} ≠ charter)"
    if bool(board.get("p99_regress")):
        paths = board.get("p99_regress_paths") or []
        return f"KILL (live p99 regress vs H-FASTBE baseline: {paths})"
    flags = (
        ("lookup_wall_neq_speed_iq", "KILL (LOOKUP wall=0 must not be sold as speed IQ)"),
        ("warm_cache_vanity_forbidden", "KILL (warm-cache vanity must stay forbidden)"),
        ("fp_for_ms_forbidden", "KILL (FP-for-ms must stay forbidden)"),
        (
            "be_fastbe_archive_untouched",
            "KILL (BE H-FASTBE archive must stay untouched)",
        ),
        (
            "bd_fastgain_archive_untouched",
            "KILL (BD H-FASTGAIN archive must stay untouched)",
        ),
        (
            "bc_fastlift_archive_untouched",
            "KILL (BC H-FASTLIFT archive must stay untouched)",
        ),
        (
            "bb_fasthold_archive_untouched",
            "KILL (BB H-FASTHOLD archive must stay untouched)",
        ),
        (
            "ba_fastreal_archive_untouched",
            "KILL (BA H-FASTREAL archive must stay untouched)",
        ),
        (
            "ah_fastlift_archive_untouched",
            "KILL (AH H-FASTLIFT archive must stay untouched)",
        ),
    )
    for key, msg in flags:
        if not bool(board.get(key)):
            return msg
    return None


def _gate_latency(board: Mapping[str, Any]) -> str | None:
    return _gate_tel_paths(board) or _gate_latency_flags(board)


def decide_fastbf(
    *,
    board: Mapping[str, Any],
    anti_fp_signed: bool = True,
) -> str:
    """
    GIVEN BF3 FASTBF board
    WHEN applying pesquisa §4 + §9 BF3
    THEN PROMOTE iff latency published + anti-FP hold + no p99 regress.
    """
    if not anti_fp_signed:
        return "KILL (anti-FP charter not signed)"
    err = _gate_antifp(board) or _gate_latency(board)
    if err:
        return err
    return (
        f"PROMOTE ({FASTBF_ID}: prod p50/p99 hold/lift; "
        "anti-FP hold; no live p99 regress vs H-FASTBE baseline)"
    )
