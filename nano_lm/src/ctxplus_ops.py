"""Wave AC1 H-CTXPLUS: multi-slice ROLL/SUMCACHE; L_eff↑ vs AB LONGAPP."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from longapp_ops import pick_best_roll_segment
from roll_ctx import iter_roll_segments
from roll_ops import MIN_LEFF_RATIO, ROLL_S, ROLL_W
from sumcache_ctx import build_sumcache_ids
from sumcache_ops import ACTIVE_CAP, MIN_LEFF, SUMCACHE_W
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "CTXPLUS_ID",
    "CTXPLUS_N",
    "TOP_K_SLICES",
    "AB_LONGAPP_MEAN_LEFF",
    "MIN_USABLE",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ROLL_W",
    "ROLL_S",
    "SUMCACHE_W",
    "ACTIVE_CAP",
    "MIN_LEFF",
    "MIN_LEFF_RATIO",
    "pick_top_roll_segments",
    "ctxplus_doc_meta",
    "score_ctxplus_trial",
    "ctxplus_stats",
    "decide_ctxplus",
]

CTXPLUS_ID = "H-CTXPLUS"
CTXPLUS_N = 10
TOP_K_SLICES = 3
# Evidence: results/nano-lm/wave-ab/longapp_summary.json mean_l_eff
AB_LONGAPP_MEAN_LEFF = 10544.9
MIN_USABLE = 7  # ≥7/10 long usable (§12.1 AC1)


def pick_top_roll_segments(
    ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    k: int = TOP_K_SLICES,
    w: int = ROLL_W,
    s: int = ROLL_S,
) -> list[dict[str, Any]]:
    """
    GIVEN full doc token ids + question token ids
    WHEN selecting multi-slice ROLL windows
    THEN return up to K segments ranked by question-token overlap.
    """
    qset = set(int(x) for x in question_ids)
    scored: list[tuple[float, dict[str, Any]]] = []
    for seg in iter_roll_segments(list(ids), w=w, s=s):
        ctx = set(int(x) for x in seg["ctx_ids"])
        sc = float(len(qset & ctx) / max(len(qset), 1)) if qset else 0.0
        out = dict(seg)
        out["overlap"] = float(sc)
        scored.append((sc, out))
    scored.sort(key=lambda t: (-t[0], int(t[1]["seg_i"])))
    n = max(1, int(k))
    return [s for _, s in scored[:n]] if scored else []


def ctxplus_doc_meta(
    ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    k: int = TOP_K_SLICES,
) -> dict[str, Any]:
    """
    GIVEN curated doc tokens + question tokens
    WHEN building CTXPLUS context
    THEN SUMCACHE + top-K ROLL slices + L_eff vs AB LONGAPP baseline.
    """
    id_list = list(ids)
    l_eff = len(id_list)
    built = build_sumcache_ids(id_list)
    slices = pick_top_roll_segments(id_list, question_ids, k=k)
    best = (
        slices[0]
        if slices
        else pick_best_roll_segment(id_list, question_ids)
    )
    union: set[int] = set()
    for seg in slices:
        union.update(int(x) for x in seg["ctx_ids"])
    single_len = int(best.get("active_len") or 0)
    union_len = len(union)
    return {
        "l_eff": int(l_eff),
        "sumcache_active": int(built["active_len"]),
        "sumcache_tail": int(built["tail_len"]),
        "sumcache_coarse": int(built["coarse_len"]),
        "sumcache_fine": int(built["fine_len"]),
        "n_slices": int(len(slices)),
        "slice_union": int(union_len),
        "best_slice_active": int(single_len),
        "roll_seg_i": int(best.get("seg_i") or 0),
        "roll_overlap": float(best.get("overlap") or 0.0),
        "multi_deeper": int(union_len) > int(single_len),
        "ratio_vs_roll_w": float(l_eff) / float(ROLL_W) if ROLL_W else 0.0,
        "ratio_vs_sum_w": (
            float(l_eff) / float(SUMCACHE_W) if SUMCACHE_W else 0.0
        ),
        "ctx_bounded": int(built["active_len"]) <= int(ACTIVE_CAP),
        "l_eff_ok": int(l_eff) >= int(MIN_LEFF),
        "ratio_ok": (float(l_eff) / float(ROLL_W)) >= float(MIN_LEFF_RATIO),
        "above_ab_leff": float(l_eff) > float(AB_LONGAPP_MEAN_LEFF),
    }


def score_ctxplus_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN CTXPLUS ask + ctx meta
    WHEN scoring HITL
    THEN (score, error, notes, usable).
    usable ⇒ score≥8 and L_eff/ratio/bounded and multi-slice present.
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
    slices_ok = int(meta.get("n_slices") or 0) >= 1
    usable = (not err) and score >= 8.0 and ctx_ok and slices_ok
    notes = list(notes) + [
        (
            f"L_eff={meta.get('l_eff')} slices={meta.get('n_slices')} "
            f"union={meta.get('slice_union')} "
            f"active={meta.get('sumcache_active')}"
        ),
        (
            "CTXPLUS multi-slice ROLL+SUMCACHE — not STREAM / naive CTX"
            if ctx_ok and slices_ok
            else "FIX: ctx/multi-slice gate failed"
        ),
    ]
    if (not ctx_ok or not slices_ok) and not err:
        return score, True, notes, False
    return score, err, notes, usable


def ctxplus_stats(
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
    mean_slices: float,
    mean_union: float,
    n_multi_deeper: int,
) -> dict[str, Any]:
    """
    GIVEN 10 CTXPLUS scores + ctx means
    WHEN summarizing H-CTXPLUS
    THEN quality + usable + L_eff↑ vs AB LONGAPP.
    """
    if len(scores) != CTXPLUS_N or len(errors) != CTXPLUS_N:
        raise ValueError(f"CTXPLUS requires exactly {CTXPLUS_N} scores/errors")
    if len(usables) != CTXPLUS_N:
        raise ValueError(f"CTXPLUS requires exactly {CTXPLUS_N} usable flags")
    mean = float(sum(scores) / float(CTXPLUS_N))
    n_err = int(sum(1 for e in errors if e))
    n_usable = int(sum(1 for u in usables if u))
    return {
        "n_trials": CTXPLUS_N,
        "mean": mean,
        "n_errors": n_err,
        "n_usable": n_usable,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "mean_l_eff": float(mean_l_eff),
        "mean_active": float(mean_active),
        "mean_ratio": float(mean_ratio),
        "mean_slices": float(mean_slices),
        "mean_union": float(mean_union),
        "n_multi_deeper": int(n_multi_deeper),
        "ab_longapp_mean_leff": float(AB_LONGAPP_MEAN_LEFF),
        "min_usable": MIN_USABLE,
        "pass_usable": n_usable >= MIN_USABLE,
        "pass_leff": float(mean_l_eff) >= float(MIN_LEFF),
        "pass_leff_up": float(mean_l_eff) > float(AB_LONGAPP_MEAN_LEFF),
        "pass_ratio": float(mean_ratio) >= float(MIN_LEFF_RATIO),
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_slices": float(mean_slices) >= 1.0,
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_ctxplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN CTXPLUS stats
    WHEN applying §8.5 / §12.1 AC1 gate
    THEN PROMOTE if usable≥7 ∧ L_eff↑ ∧ gates ∧ no false-hit;
         HOLD if no false-hit but soft-fail; KILL if false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    ok = (
        bool(stats.get("pass_usable"))
        and bool(stats.get("pass_leff"))
        and bool(stats.get("pass_leff_up"))
        and bool(stats.get("pass_ratio"))
        and bool(stats.get("pass_active"))
        and bool(stats.get("pass_slices"))
        and bool(stats.get("pass_quality"))
    )
    if ok:
        return "PROMOTE"
    return "HOLD"
