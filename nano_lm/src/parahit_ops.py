"""Wave AQ1 H-PARAHIT: human paraphrase hit-rate on SEMWRAP (AQ0 pack)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aq_session_ops import AQ0_PARA_N, AQ0_PARA_PACK, para_collides_parent_norm
from semwrap_ops import score_semwrap_trial
from z_wrap import normalize_question

__all__ = [
    "PARAHIT_ID",
    "PARAHIT_N",
    "PARAHIT_PACK",
    "MIN_HIT_RATE",
    "MIN_MEAN",
    "PARAHIT_THESIS",
    "pack_ok",
    "miss_ids",
    "parahit_stats",
    "decide_parahit",
    "score_parahit_trial",
]

PARAHIT_ID = "H-PARAHIT"
PARAHIT_N = AQ0_PARA_N  # 20 — frozen AQ0 paraphrase pack
PARAHIT_PACK = AQ0_PARA_PACK
MIN_HIT_RATE = 0.70  # ≥14/20 TRUE_HIT for PROMOTE
MIN_MEAN = 7.0
PARAHIT_THESIS = (
    "Human paraphrase hit-rate on SEMWRAP over AQ0 paraphrase-20; "
    "false-hit 0; report misses; not LOOKUP-as-IQ / not bank-expansion theater"
)


def pack_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AQ0 paraphrase pack
    WHEN validating PARAHIT inputs
    THEN True iff N=20, unique ids, paraphrase≠parent normalize.
    """
    rows = list(pack) if pack is not None else list(PARAHIT_PACK)
    if len(rows) != PARAHIT_N:
        return False
    ids = [str(p.get("id", "")).strip() for p in rows]
    if len(set(ids)) != PARAHIT_N or not all(ids):
        return False
    if para_collides_parent_norm(rows):
        return False
    for item in rows:
        if not str(item.get("paraphrase", "")).strip():
            return False
        if not str(item.get("gold", "")).strip():
            return False
        if not str(item.get("parent_question", "")).strip():
            return False
    return True


def score_parahit_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN SEMWRAP paraphrase ask
    WHEN scoring product HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; MISS documented (no generative IQ claim).
    """
    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + [
        "PARAHIT product SEMWRAP paraphrase — labeled LOOKUP, not generative IQ",
    ]
    return score, err, notes


def miss_ids(trials: Sequence[Mapping[str, Any]]) -> list[str]:
    """
    GIVEN PARAHIT trials
    WHEN listing non-TRUE_HIT
    THEN return trial ids (MISS or FALSE_HIT) for the miss report.
    """
    out: list[str] = []
    for t in trials:
        if str(t.get("lookup_kind", "")) != "TRUE_HIT":
            out.append(str(t.get("trial_id", "")))
    return [x for x in out if x]


def parahit_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
) -> dict[str, Any]:
    """
    GIVEN 20 PARAHIT scores
    WHEN summarizing AQ1
    THEN hit_rate · mean · false-hit · pass flags.
    """
    if len(scores) != PARAHIT_N or len(errors) != PARAHIT_N:
        raise ValueError(f"PARAHIT requires exactly {PARAHIT_N} scores/errors")
    mean = float(sum(scores) / float(PARAHIT_N))
    n_err = int(sum(1 for e in errors if e))
    hit_rate = float(n_true_hit) / float(PARAHIT_N)
    return {
        "n_trials": PARAHIT_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "hit_rate": round(hit_rate, 4),
        "min_hit_rate": MIN_HIT_RATE,
        "min_mean": MIN_MEAN,
        "pass_hit_rate": hit_rate >= MIN_HIT_RATE,
        "pass_mean": mean >= MIN_MEAN,
        "pass_false_hit": int(n_false_hit) == 0,
    }


def decide_parahit(stats: Mapping[str, Any]) -> str:
    """
    GIVEN PARAHIT stats
    WHEN applying pesquisa §5 AQ1 gate
    THEN KILL if false-hit>0; PROMOTE if hit≥bar ∧ mean≥7; else HOLD.
    """
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    if bool(stats.get("pass_hit_rate")) and bool(stats.get("pass_mean")):
        return "PROMOTE"
    return "HOLD"


def parent_already_normalized(
    bank_questions: set[str], parent: str
) -> bool:
    """True if parent question already present under normalize_question."""
    key = normalize_question(parent)
    return any(normalize_question(q) == key for q in bank_questions)
