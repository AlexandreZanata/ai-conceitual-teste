"""Wave AR4 H-ADVREG: adversary regression + SAFE≠quality (AR0 pack)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aq_session_ops import ADV_KINDS
from ar_session_ops import (
    AR0_ADVREG_N,
    AR0_ADVREG_PACK,
    AR0_SAFE_NOTE,
    advreg_kind_counts,
    advreg_overlaps_aq_adv,
)
from advfp_ops import score_advfp_trial

__all__ = [
    "ADVREG_ID",
    "ADVREG_N",
    "ADVREG_PACK",
    "ADVREG_THESIS",
    "FORBIDDEN_NEEDLES",
    "SAFE_NOTE",
    "pack_ok",
    "classify_advreg",
    "score_advreg_trial",
    "false_hit_ids",
    "advreg_stats",
    "decide_advreg",
]

ADVREG_ID = "H-ADVREG"
ADVREG_N = AR0_ADVREG_N
ADVREG_PACK = AR0_ADVREG_PACK
SAFE_NOTE = AR0_SAFE_NOTE
ADVREG_THESIS = (
    "Adversary regression (AR0 advreg-20 ≠ AQ-ADV exact text) must keep "
    "SEMWRAP false-hit 0; SAFE≠answer-quality documented — not generative IQ"
)

# Near-miss: needles that mean SEMWRAP returned the trap/wrong parent gold.
FORBIDDEN_NEEDLES: Mapping[str, tuple[str, ...]] = {
    "AR-ADVREG-01": ("cs = ent / 32", "cs=ent/32"),
    "AR-ADVREG-02": ("0x00000000",),
    "AR-ADVREG-03": ("p2wpkh",),
    "AR-ADVREG-04": ("append",),
    "AR-ADVREG-05": ("pass",),
    "AR-ADVREG-06": ("isize", "usize"),
    "AR-ADVREG-07": ("secp256k1",),
    "AR-ADVREG-08": ("/rest/tx/", "block-hash", "block/<"),
}


def _ids_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    ids = [str(p.get("id", "")).strip() for p in rows]
    if len(set(ids)) != ADVREG_N or not all(ids):
        return False
    return all(i.startswith("AR-ADVREG-") for i in ids)


def _asks_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    for item in rows:
        if str(item.get("expect", "")) != "no_false_hit":
            return False
        if str(item.get("kind", "")) not in ADV_KINDS:
            return False
        ask = str(item.get("ask", ""))
        tid = str(item.get("id", ""))
        if tid == "AR-ADVREG-19":
            if ask.strip():
                return False
        elif not ask.strip():
            return False
    return True


def pack_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AR0 advreg pack
    WHEN validating ADVREG inputs
    THEN True iff N=20, ≠ AQ-ADV exact ask, kinds present, expect=no_false_hit.
    """
    rows = list(pack) if pack is not None else list(ADVREG_PACK)
    if len(rows) != ADVREG_N or not _ids_ok(rows):
        return False
    if advreg_overlaps_aq_adv(rows):
        return False
    kinds = advreg_kind_counts(rows)
    if set(kinds) != ADV_KINDS or any(kinds.get(k, 0) < 1 for k in ADV_KINDS):
        return False
    return _asks_ok(rows)


def classify_advreg(
    *,
    item: Mapping[str, str],
    looked_up: str | None,
) -> str:
    """
    GIVEN SEMWRAP result on an ADVREG ask
    WHEN classifying safety
    THEN FALSE_HIT if silent wrong gold (or any gold on OOD/trap); else SAFE.
    """
    text = str(looked_up or "").strip()
    if not text:
        return "SAFE"
    kind = str(item.get("kind", ""))
    if kind in {"ood", "trap"}:
        return "FALSE_HIT"
    needles = FORBIDDEN_NEEDLES.get(str(item.get("id", "")), ())
    low = text.lower()
    if any(n in low for n in needles):
        return "FALSE_HIT"
    return "SAFE"


def score_advreg_trial(
    *,
    mode: str,
    kind: str,
    outcome: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN ADVREG classify outcome
    WHEN scoring
    THEN FALSE_HIT→0; SAFE→9 + SAFE≠quality note (mean not sold as IQ).
    """
    score, err, notes = score_advfp_trial(mode=mode, kind=kind, outcome=outcome)
    notes = list(notes) + [
        SAFE_NOTE,
        "ADVREG regression — mean/SAFE is not answer quality / generative IQ",
    ]
    return score, err, notes


def false_hit_ids(trials: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return trial ids classified FALSE_HIT."""
    return [
        str(t.get("trial_id", ""))
        for t in trials
        if str(t.get("outcome", "")) == "FALSE_HIT" and t.get("trial_id")
    ]


def advreg_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_safe: int,
    n_false_hit: int,
    kind_false: Mapping[str, int],
) -> dict[str, Any]:
    """
    GIVEN 20 ADVREG scores
    WHEN summarizing AR4
    THEN false-hit count + SAFE≠quality flag + pass.
    """
    if len(scores) != ADVREG_N or len(errors) != ADVREG_N:
        raise ValueError(f"ADVREG requires exactly {ADVREG_N} scores/errors")
    mean = float(sum(scores) / float(ADVREG_N))
    return {
        "n_trials": ADVREG_N,
        "mean": mean,
        "mean_is_quality": False,
        "safe_note": SAFE_NOTE,
        "n_errors": int(sum(1 for e in errors if e)),
        "n_safe": int(n_safe),
        "n_false_hit": int(n_false_hit),
        "false_hit_by_kind": dict(kind_false),
        "pass_false_hit": int(n_false_hit) == 0,
    }


def decide_advreg(stats: Mapping[str, Any]) -> str:
    """
    GIVEN ADVREG stats
    WHEN applying pesquisa §5 AR4 gate
    THEN PROMOTE iff false-hit 0 and SAFE≠quality documented; else KILL.
    """
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    if bool(stats.get("mean_is_quality")):
        return "KILL (mean sold as answer quality)"
    note = str(stats.get("safe_note", ""))
    if "≠" not in note and "!=" not in note:
        return "KILL (SAFE≠quality note missing)"
    return "PROMOTE"
