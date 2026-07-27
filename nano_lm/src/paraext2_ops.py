"""Wave AS4 H-PARAEXT2: external paraphrase hit-rate after SEMFIX (AS0 pack)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from as_session_ops import (
    AS0_PARA_N,
    AS0_PARAEXT2_PACK,
    paraext2_collides_parent_norm,
    paraext2_overlaps_ap_hitl,
    paraext2_overlaps_aq_para,
    paraext2_overlaps_ar_ext,
)
from paraext_ops import parent_already_normalized, score_paraext_trial

__all__ = [
    "PARAEXT2_ID",
    "PARAEXT2_N",
    "PARAEXT2_PACK",
    "MIN_HIT_RATE",
    "MIN_MEAN",
    "PARAEXT2_THESIS",
    "pack_ok",
    "miss_ids",
    "paraext2_stats",
    "decide_paraext2",
    "score_paraext2_trial",
    "parent_already_normalized",
]

PARAEXT2_ID = "H-PARAEXT2"
PARAEXT2_N = AS0_PARA_N
PARAEXT2_PACK = AS0_PARAEXT2_PACK
MIN_HIT_RATE = 0.70
MIN_MEAN = 7.0
PARAEXT2_THESIS = (
    "Fresh AS0 PARAEXT2-20 paraphrases (≠ AQ-PARA / AR-EXT / AP-HITL text) "
    "hit-rate on SEMWRAP after SEMFIX; false-hit 0; report misses; not LOOKUP-as-IQ"
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
    if len(set(ids)) != PARAEXT2_N or not all(ids):
        return False
    return all(i.startswith("AS-EXT2-") for i in ids)


def pack_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AS0 PARAEXT2 pack
    WHEN validating PARAEXT2 inputs
    THEN True iff N=20, disjoint from AQ/AR/AP packs, paraphrase≠parent.
    """
    rows = list(pack) if pack is not None else list(PARAEXT2_PACK)
    if len(rows) != PARAEXT2_N or not _ids_ok(rows):
        return False
    if paraext2_collides_parent_norm(rows):
        return False
    if paraext2_overlaps_aq_para(rows) or paraext2_overlaps_ar_ext(rows):
        return False
    if paraext2_overlaps_ap_hitl(rows):
        return False
    return _fields_ok(rows)


def score_paraext2_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN SEMWRAP PARAEXT2 ask
    WHEN scoring product HITL
    THEN reuse PARAEXT score + AS4 anti-FP notes.
    """
    score, err, notes = score_paraext_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    notes = list(notes) + [
        "PARAEXT2 after SEMFIX — labeled LOOKUP, not generative IQ",
        "pack ≠ AQ-PARA / AR-EXT / AP-HITL exact text",
        "no paraphrase bank expand (anti theater)",
    ]
    return score, err, notes


def miss_ids(trials: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return trial ids that are not TRUE_HIT."""
    out: list[str] = []
    for t in trials:
        if str(t.get("lookup_kind", "")) != "TRUE_HIT":
            out.append(str(t.get("trial_id", "")))
    return [x for x in out if x]


def paraext2_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
) -> dict[str, Any]:
    """
    GIVEN 20 PARAEXT2 scores
    WHEN summarizing AS4
    THEN hit_rate · mean · false-hit · pass flags.
    """
    if len(scores) != PARAEXT2_N or len(errors) != PARAEXT2_N:
        raise ValueError(
            f"PARAEXT2 requires exactly {PARAEXT2_N} scores/errors"
        )
    mean = float(sum(scores) / float(PARAEXT2_N))
    n_err = int(sum(1 for e in errors if e))
    hit_rate = float(n_true_hit) / float(PARAEXT2_N)
    return {
        "n_trials": PARAEXT2_N,
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


def decide_paraext2(stats: Mapping[str, Any]) -> str:
    """
    GIVEN PARAEXT2 stats
    WHEN applying pesquisa §5 AS4 gate
    THEN KILL if false-hit>0; PROMOTE if hit≥bar ∧ mean≥7; else HOLD.
    """
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    if bool(stats.get("pass_hit_rate")) and bool(stats.get("pass_mean")):
        return "PROMOTE"
    return "HOLD"
