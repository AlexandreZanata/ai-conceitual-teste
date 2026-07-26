"""Wave AI1b H-CAPRENEG: named size+budget renegotiate after GENPLUS HOLD."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ai_session_ops import AI0_PACK
from genplus_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    score_genplus_gen,
    score_genplus_lookup,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "CAPRENEG_ID",
    "CAPRENEG_N",
    "CAPRENEG_PACK",
    "HARD_CAP_PARAMS",
    "PROPOSAL_ID",
    "PROPOSED_MAX_PARAMS",
    "PROBE_HF_ID",
    "PROBE_TOKENIZER_ID",
    "BUDGET_WALL_S",
    "BUDGET_VRAM_GB",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENPLUS_GEN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "score_capreneg_lookup",
    "score_capreneg_gen",
    "proposal_ok",
    "budget_ok",
    "capreneg_stats",
    "decide_capreneg",
]

CAPRENEG_ID = "H-CAPRENEG"
CAPRENEG_N = 10
# Current hard law until this stage PROMOTE.
HARD_CAP_PARAMS = 5_000_000
# Named renegotiation (pesquisa §5 AI1b).
PROPOSAL_ID = "CAP-125M"
# Ceiling for the GPT-Neo-125M HF class (~125.2M measured weights).
PROPOSED_MAX_PARAMS = 130_000_000
PROBE_HF_ID = "EleutherAI/gpt-neo-125M"
PROBE_TOKENIZER_ID = "EleutherAI/gpt-neo-125M"
BUDGET_WALL_S = 600
BUDGET_VRAM_GB = 8
GENPLUS_GEN_MEAN = 4.0  # AI1 HOLD ceiling that triggered this stage

CAPRENEG_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AI0_PACK
)


def score_capreneg_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve; ≠ generative IQ / ≠ size claim."""
    score, err, notes = score_genplus_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = list(notes) + [
        "CAPRENEG LOOKUP uses ≤5M product path — not size PROMOTE alone",
    ]
    return float(score), bool(err), notes


def score_capreneg_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """GENERATE arm on named probe — Cursor completion score; wall_ms>0."""
    score, err, notes = score_genplus_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
    )
    notes = list(notes) + [
        f"CAPRENEG probe={PROBE_HF_ID} proposal={PROPOSAL_ID}",
        f"beat GENPLUS gen={GENPLUS_GEN_MEAN} required for size PROMOTE",
    ]
    return float(score), bool(err), notes


def proposal_ok(
    *,
    proposed_max: int,
    probe_params: int,
    hard_cap: int = HARD_CAP_PARAMS,
) -> bool:
    """
    GIVEN named size proposal + measured probe params
    WHEN validating CAPRENEG
    THEN True iff proposed>hard ∧ 0<probe≤proposed.
    """
    if int(proposed_max) <= int(hard_cap):
        return False
    if int(probe_params) <= 0:
        return False
    return int(probe_params) <= int(proposed_max)


def budget_ok(
    *,
    elapsed_s: float,
    vram_gb_peak: float,
    wall_s_max: float = BUDGET_WALL_S,
    vram_gb_max: float = BUDGET_VRAM_GB,
    weight_update: bool,
) -> bool:
    """
    GIVEN run telemetry
    WHEN checking named budget
    THEN True iff wall/vram within cap and no weight update.
    """
    if bool(weight_update):
        return False
    if float(elapsed_s) > float(wall_s_max):
        return False
    if float(vram_gb_peak) > float(vram_gb_max):
        return False
    return True


def capreneg_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
    champion_params: int,
    probe_params: int,
    elapsed_s: float,
    vram_gb_peak: float,
    weight_update: bool,
) -> dict[str, Any]:
    """
    GIVEN dual-arm + size telemetry
    WHEN summarizing H-CAPRENEG
    THEN means + proposal/budget flags + gen≥5 pass.
    """
    if len(lookup_scores) != CAPRENEG_N or len(gen_scores) != CAPRENEG_N:
        raise ValueError(f"CAPRENEG requires {CAPRENEG_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(CAPRENEG_N))
    g_mean = float(sum(gen_scores) / float(CAPRENEG_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    prop = proposal_ok(
        proposed_max=PROPOSED_MAX_PARAMS, probe_params=int(probe_params)
    )
    bud = budget_ok(
        elapsed_s=float(elapsed_s),
        vram_gb_peak=float(vram_gb_peak),
        weight_update=bool(weight_update),
    )
    return {
        "n_trials": CAPRENEG_N,
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
        "genplus_gen_mean": GENPLUS_GEN_MEAN,
        "hard_cap_params": HARD_CAP_PARAMS,
        "proposal_id": PROPOSAL_ID,
        "proposed_max_params": PROPOSED_MAX_PARAMS,
        "probe_hf_id": PROBE_HF_ID,
        "champion_params": int(champion_params),
        "probe_params": int(probe_params),
        "elapsed_s": float(elapsed_s),
        "vram_gb_peak": float(vram_gb_peak),
        "budget_wall_s": BUDGET_WALL_S,
        "budget_vram_gb": BUDGET_VRAM_GB,
        "proposal_ok": prop,
        "budget_ok": bud,
        "champion_within_hard_cap": int(champion_params) <= HARD_CAP_PARAMS,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_genplus_gen": g_mean > GENPLUS_GEN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "weight_update": bool(weight_update),
    }


def decide_capreneg(stats: Mapping[str, Any]) -> str:
    """
    GIVEN CAPRENEG dual-arm + size stats
    WHEN applying pesquisa §5 AI1b gate
    THEN KILL if false-hit/bad proposal;
         PROMOTE iff lookup+gen≥5+proposal+budget (raise hard cap);
         else HOLD (keep ≤5M).
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    if not bool(stats.get("champion_within_hard_cap")):
        return "KILL (champion already above hard cap)"
    if not bool(stats.get("proposal_ok")):
        return "KILL (invalid named size proposal)"
    if bool(stats.get("pass_lookup")) and bool(stats.get("pass_gen")):
        if bool(stats.get("budget_ok")):
            return "PROMOTE"
        return "HOLD"
    return "HOLD"
