"""Wave AR3 H-PARAEXT: external paraphrase hit-rate on SEMWRAP (AR0 pack)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ar_session_ops import (
    AR0_EXT_N,
    AR0_EXT_PARA_PACK,
    ext_collides_parent_norm,
    ext_overlaps_aq_para,
)
from parahit_ops import score_parahit_trial
from z_wrap import normalize_question

__all__ = [
    "PARAEXT_ID",
    "PARAEXT_N",
    "PARAEXT_PACK",
    "MIN_HIT_RATE",
    "MIN_MEAN",
    "PARAEXT_THESIS",
    "pack_ok",
    "miss_ids",
    "paraext_stats",
    "decide_paraext",
    "score_paraext_trial",
    "parent_already_normalized",
]

PARAEXT_ID = "H-PARAEXT"
PARAEXT_N = AR0_EXT_N  # 20 — frozen AR0 external-para pack
PARAEXT_PACK = AR0_EXT_PARA_PACK
MIN_HIT_RATE = 0.70  # ≥14/20 TRUE_HIT for PROMOTE (same bar as PARAHIT)
MIN_MEAN = 7.0
PARAEXT_THESIS = (
    "Fresh external/human paraphrases (AR0 external-para-20 ≠ AQ-PARA text) "
    "hit-rate on SEMWRAP; false-hit 0; report misses; not LOOKUP-as-IQ"
)


def _fields_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    for item in rows:
        if not str(item.get("paraphrase", "")).strip():
            return False
        if not str(item.get("gold", "")).strip():
            return False
        if not str(item.get("parent_question", "")).strip():
            return False
    return True


def _ids_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    ids = [str(p.get("id", "")).strip() for p in rows]
    if len(set(ids)) != PARAEXT_N or not all(ids):
        return False
    return all(i.startswith("AR-EXT-") for i in ids)


def pack_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AR0 external-para pack
    WHEN validating PARAEXT inputs
    THEN True iff N=20, ≠ AQ-PARA exact text, paraphrase≠parent normalize.
    """
    rows = list(pack) if pack is not None else list(PARAEXT_PACK)
    if len(rows) != PARAEXT_N:
        return False
    if not _ids_ok(rows):
        return False
    if ext_collides_parent_norm(rows) or ext_overlaps_aq_para(rows):
        return False
    return _fields_ok(rows)


def score_paraext_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN SEMWRAP external-paraphrase ask
    WHEN scoring product HITL
    THEN FALSE_HIT→0; TRUE_HIT→9; MISS documented (no generative IQ claim).
    """
    score, err, notes = score_parahit_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + [
        "PARAEXT external paraphrase SEMWRAP — labeled LOOKUP, not generative IQ",
        "pack ≠ AQ-PARA exact text (anti AQ0 replay)",
    ]
    return score, err, notes


def miss_ids(trials: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return trial ids that are not TRUE_HIT."""
    out: list[str] = []
    for t in trials:
        if str(t.get("lookup_kind", "")) != "TRUE_HIT":
            out.append(str(t.get("trial_id", "")))
    return [x for x in out if x]


def paraext_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
) -> dict[str, Any]:
    """
    GIVEN 20 PARAEXT scores
    WHEN summarizing AR3
    THEN hit_rate · mean · false-hit · pass flags.
    """
    if len(scores) != PARAEXT_N or len(errors) != PARAEXT_N:
        raise ValueError(f"PARAEXT requires exactly {PARAEXT_N} scores/errors")
    mean = float(sum(scores) / float(PARAEXT_N))
    n_err = int(sum(1 for e in errors if e))
    hit_rate = float(n_true_hit) / float(PARAEXT_N)
    return {
        "n_trials": PARAEXT_N,
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


def decide_paraext(stats: Mapping[str, Any]) -> str:
    """
    GIVEN PARAEXT stats
    WHEN applying pesquisa §5 AR3 gate
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
