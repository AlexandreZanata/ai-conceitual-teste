"""Wave AH6 AH-HITL-10: final dual-arm verify on frozen AH0 pack."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "AH6_ID",
    "AH6_N",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "DECLARED_STACK",
    "STACK_CLAIM",
    "SHIP_CLAIM_AF",
    "claim_is_honest",
    "score_ah6_lookup",
    "score_ah6_gen",
    "ah6_stats",
    "decide_ah6",
]

AH6_ID = "AH-HITL-10"
AH6_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0
# Declared AH wave stack (lift spines + AF product inherit).
DECLARED_STACK: tuple[str, ...] = (
    "H-GENLIFT",
    "H-CTXLIFT",
    "H-SMARTLIFT",
    "H-FASTLIFT",
    "H-APPLIFT",
    "H-SEMWRAP",
    "H-ASKFAST",
)
STACK_CLAIM = (
    "scoped AH dual-arm verify on AF packaged stack — "
    "LOOKUP ≠ generative IQ; not open chat LM"
)
SHIP_CLAIM_AF = (
    "scoped AF packaged stack — not open chat LM "
    "(AH gen arm below bar; ship claim unchanged)"
)


def claim_is_honest(claim: str) -> bool:
    low = str(claim).lower()
    if "open chat" in low and "not open chat" not in low:
        return False
    return "scoped" in low or "packaged" in low or "dual-arm" in low


def score_ah6_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN LOOKUP arm on final AH pack
    WHEN Cursor EVAL
    THEN product score; labeled ≠ generative IQ.
    """
    from askfast_ops import score_askfast_trial

    score, err, notes = score_askfast_trial(
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
        "AH6 LOOKUP final — not generative IQ",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_ah6_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm on final AH pack
    WHEN Cursor EVAL
    THEN require wall_ms>0 ∧ n_new>0; score completion honestly.
    """
    from antifp_ops import score_antifp_completion

    score, err, notes = score_antifp_completion(
        arm="GENERATE",
        completion=completion,
        gold=expected_gold,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "AH6 GENERATE final — Cursor scores completion",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen wall_ms/n_new required"]
    return float(score), bool(err), notes


def ah6_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_gen_wall_ok: int,
    n_fix: int,
    claim_ok: bool,
    held_out_ok: bool,
    n_known: int,
    n_howto: int,
    n_long: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm final HITL
    WHEN summarizing AH6
    THEN lookup≥7 · errors≤3/arm · gen≥5 or HOLD path · held-out ok.
    """
    if len(lookup_scores) != AH6_N or len(gen_scores) != AH6_N:
        raise ValueError(f"AH6 requires {AH6_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(AH6_N))
    g_mean = float(sum(gen_scores) / float(AH6_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    return {
        "n_trials": AH6_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_gen_wall_ok": int(n_gen_wall_ok),
        "n_fix": int(n_fix),
        "claim_ok": bool(claim_ok),
        "held_out_ok": bool(held_out_ok),
        "n_known": int(n_known),
        "n_howto": int(n_howto),
        "n_long": int(n_long),
        "dual_arm": True,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS
        and int(n_false_hit) == 0,
        "pass_gen": g_mean >= MIN_GEN_MEAN
        and n_g_err <= PASS_MAX_ERRORS,
        "pass_gen_telemetry": int(n_gen_wall_ok) >= AH6_N,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "stack": list(DECLARED_STACK),
    }


def decide_ah6(stats: Mapping[str, Any]) -> str:
    """
    GIVEN AH6 final dual-arm stats
    WHEN applying pesquisa §5 AH6 gate
    THEN KILL if false-hit/held-out/telemetry fail;
         PROMOTE if lookup∧gen≥5; HOLD if lookup ok + gen soft (documented).
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("held_out_ok")):
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    if not bool(stats.get("pass_gen_telemetry")):
        return "KILL"
    if not bool(stats.get("pass_lookup")):
        return "KILL"
    if not bool(stats.get("claim_ok")):
        return "HOLD"
    if bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
