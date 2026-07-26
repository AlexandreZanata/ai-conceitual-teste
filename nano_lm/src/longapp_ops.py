"""Wave AB3 H-LONGAPP: ROLL/SUMCACHE windows on curated long docs."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from roll_ctx import iter_roll_segments
from roll_ops import MIN_LEFF_RATIO, ROLL_S, ROLL_W
from sumcache_ctx import build_sumcache_ids
from sumcache_ops import ACTIVE_CAP, MIN_LEFF, SUMCACHE_W
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "LONGAPP_ID",
    "LONGAPP_N",
    "MIN_USABLE",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ROLL_W",
    "ROLL_S",
    "SUMCACHE_W",
    "ACTIVE_CAP",
    "MIN_LEFF",
    "MIN_LEFF_RATIO",
    "pick_best_roll_segment",
    "longapp_doc_meta",
    "score_longapp_trial",
    "longapp_stats",
    "decide_longapp",
]

LONGAPP_ID = "H-LONGAPP"
LONGAPP_N = 10
MIN_USABLE = 7  # ≥7/10 long usable


def pick_best_roll_segment(
    ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    w: int = ROLL_W,
    s: int = ROLL_S,
) -> dict[str, Any]:
    """
    GIVEN full doc token ids + question token ids
    WHEN selecting a ROLL window
    THEN return the segment with max token overlap (in-lab; not open web).
    """
    qset = set(int(x) for x in question_ids)
    segs = iter_roll_segments(list(ids), w=w, s=s)
    if not segs:
        return {
            "l_eff": 0,
            "active_len": 0,
            "summary_len": 0,
            "window_len": 0,
            "seg_i": 0,
            "ctx_ids": [],
            "overlap": 0.0,
        }
    best = segs[0]
    best_sc = -1.0
    for seg in segs:
        ctx = set(int(x) for x in seg["ctx_ids"])
        sc = float(len(qset & ctx) / max(len(qset), 1)) if qset else 0.0
        if sc > best_sc:
            best_sc = sc
            best = seg
    out = dict(best)
    out["overlap"] = float(best_sc)
    return out


def longapp_doc_meta(
    ids: Sequence[int],
    question_ids: Sequence[int],
) -> dict[str, Any]:
    """
    GIVEN curated doc tokens + question tokens
    WHEN building LONGAPP context
    THEN SUMCACHE active window + best ROLL segment + L_eff ratios.
    """
    id_list = list(ids)
    l_eff = len(id_list)
    built = build_sumcache_ids(id_list)
    roll = pick_best_roll_segment(id_list, question_ids)
    return {
        "l_eff": int(l_eff),
        "sumcache_active": int(built["active_len"]),
        "sumcache_tail": int(built["tail_len"]),
        "sumcache_coarse": int(built["coarse_len"]),
        "sumcache_fine": int(built["fine_len"]),
        "roll_active": int(roll["active_len"]),
        "roll_seg_i": int(roll["seg_i"]),
        "roll_overlap": float(roll["overlap"]),
        "ratio_vs_roll_w": float(l_eff) / float(ROLL_W) if ROLL_W else 0.0,
        "ratio_vs_sum_w": (
            float(l_eff) / float(SUMCACHE_W) if SUMCACHE_W else 0.0
        ),
        "ctx_bounded": int(built["active_len"]) <= int(ACTIVE_CAP),
        "l_eff_ok": int(l_eff) >= int(MIN_LEFF),
        "ratio_ok": (float(l_eff) / float(ROLL_W)) >= float(MIN_LEFF_RATIO),
    }


def score_longapp_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN LONGAPP ask + ctx meta
    WHEN scoring HITL
    THEN return (score, error, notes, usable).
    usable ⇒ score≥8 and L_eff≫W and bounded active.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    ctx_ok = bool(meta.get("l_eff_ok")) and bool(meta.get("ratio_ok"))
    ctx_ok = ctx_ok and bool(meta.get("ctx_bounded"))
    usable = (not err) and score >= 8.0 and ctx_ok
    notes = list(notes) + [
        f"L_eff={meta.get('l_eff')} active={meta.get('sumcache_active')} "
        f"ratio_W={float(meta.get('ratio_vs_roll_w') or 0):.1f}",
        (
            "LONGAPP window bounded (SUMCACHE/ROLL) — not STREAM / naive CTX"
            if ctx_ok
            else "FIX: ctx gate failed (L_eff/active)"
        ),
    ]
    if not ctx_ok and not err:
        # Quality ok but context machinery failed → still an error for AB3.
        return score, True, notes, False
    return score, err, notes, usable


def longapp_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    usables: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    mean_l_eff: float,
    mean_active: float,
    mean_ratio: float,
) -> dict[str, Any]:
    """
    GIVEN 10 LONGAPP scores + ctx means
    WHEN summarizing H-LONGAPP
    THEN quality + usable count + L_eff gates.
    """
    if len(scores) != LONGAPP_N or len(errors) != LONGAPP_N:
        raise ValueError(f"LONGAPP requires exactly {LONGAPP_N} scores/errors")
    if len(usables) != LONGAPP_N:
        raise ValueError(f"LONGAPP requires exactly {LONGAPP_N} usable flags")
    mean = float(sum(scores) / float(LONGAPP_N))
    n_err = int(sum(1 for e in errors if e))
    n_usable = int(sum(1 for u in usables if u))
    return {
        "n_trials": LONGAPP_N,
        "mean": mean,
        "n_errors": n_err,
        "n_usable": n_usable,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "mean_l_eff": float(mean_l_eff),
        "mean_active": float(mean_active),
        "mean_ratio": float(mean_ratio),
        "min_usable": MIN_USABLE,
        "pass_usable": n_usable >= MIN_USABLE,
        "pass_leff": float(mean_l_eff) >= float(MIN_LEFF),
        "pass_ratio": float(mean_ratio) >= float(MIN_LEFF_RATIO),
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_longapp(stats: Mapping[str, Any]) -> str:
    """
    GIVEN LONGAPP stats
    WHEN applying §8.3 AB3 gate
    THEN PROMOTE if usable≥7 ∧ L_eff gates ∧ no false-hit;
         HOLD if no false-hit but gates soft-fail;
         KILL if false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    ok = (
        bool(stats.get("pass_usable"))
        and bool(stats.get("pass_leff"))
        and bool(stats.get("pass_ratio"))
        and bool(stats.get("pass_active"))
        and bool(stats.get("pass_quality"))
    )
    if ok:
        return "PROMOTE"
    return "HOLD"
