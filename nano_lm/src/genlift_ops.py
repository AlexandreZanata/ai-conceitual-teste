"""Wave AH1 H-GENLIFT: lift generative completions (dual-arm anti-FP)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ah_session_ops import AH0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import (
    SERVEALIGN_MEAN,
    is_period_collapse,
    strip_stop,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "GENLIFT_ID",
    "GENLIFT_N",
    "GENLIFT_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "SMARTREAL_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "score_genlift_lookup",
    "score_genlift_gen",
    "genlift_stats",
    "decide_genlift",
]

GENLIFT_ID = "H-GENLIFT"
GENLIFT_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §5 AH1 — or honest HOLD
# Parent Wave AG SMARTREAL open-gen ceiling under score_open_completion.
SMARTREAL_GEN_MEAN = 4.0

# AH0 held-out pack (same questions for both arms).
GENLIFT_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AH0_PACK
)


def score_genlift_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN LOOKUP arm ask
    WHEN Cursor EVAL
    THEN (score, error, notes); LOOKUP ≠ generative IQ.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "GENLIFT LOOKUP product retrieve — not generative IQ",
        f"lookup_kind={lookup_kind}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_genlift_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (QPFB2+BEAMKV+anti-period)
    WHEN Cursor EVAL completion vs gold
    THEN score via open-completion rubric (not ASKSMART floor-5 on gibberish);
         require gen telemetry. Anti-period may lift past period=1.0.
    """
    from servealign_ops import score_open_completion

    text = strip_stop(completion)
    score, err, notes = score_open_completion(text, expected_gold)
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    period = is_period_collapse(text)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']} period={period}",
        "GENLIFT gen ASKSMART polish — Cursor scores completion (not LOOKUP IQ)",
        f"beat SMARTREAL gen={SMARTREAL_GEN_MEAN} / SERVEALIGN={SERVEALIGN_MEAN}",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen telemetry fail"]
    return float(score), bool(err) or period, notes


def genlift_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm scores
    WHEN summarizing H-GENLIFT
    THEN means + pass flags vs LOOKUP≥7 / GEN≥5.
    """
    if len(lookup_scores) != GENLIFT_N or len(gen_scores) != GENLIFT_N:
        raise ValueError(f"GENLIFT requires {GENLIFT_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(GENLIFT_N))
    g_mean = float(sum(gen_scores) / float(GENLIFT_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    return {
        "n_trials": GENLIFT_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_period": int(n_period),
        "n_fix": int(n_fix),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "smartreal_gen_mean": SMARTREAL_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_smartreal_gen": g_mean > SMARTREAL_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_genlift(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENLIFT dual-arm stats
    WHEN applying pesquisa §5 AH1 gate
    THEN KILL if false-hit; PROMOTE if lookup+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    if bool(stats.get("pass_lookup")) and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
