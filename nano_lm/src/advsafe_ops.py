"""Wave AS3 H-ADVSAFE: adversary regression after SEMFIX (AS0 ADVSAFE pack)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from advfp_ops import score_advfp_trial
from aq_session_ops import ADV_KINDS
from as_session_ops import (
    AS0_ADVSAFE_N,
    AS0_ADVSAFE_PACK,
    AS0_REQUIRED_ADV_PARENTS,
    AS0_SAFE_NOTE,
    advsafe_kind_counts,
    advsafe_missing_required_parents,
)

__all__ = [
    "ADVSAFE_ID",
    "ADVSAFE_N",
    "ADVSAFE_PACK",
    "ADVSAFE_THESIS",
    "FORBIDDEN_NEEDLES",
    "SAFE_NOTE",
    "REQUIRED_PARENTS",
    "pack_ok",
    "classify_advsafe",
    "score_advsafe_trial",
    "false_hit_ids",
    "advsafe_stats",
    "decide_advsafe",
]

ADVSAFE_ID = "H-ADVSAFE"
ADVSAFE_N = AS0_ADVSAFE_N
ADVSAFE_PACK = AS0_ADVSAFE_PACK
SAFE_NOTE = AS0_SAFE_NOTE
REQUIRED_PARENTS = AS0_REQUIRED_ADV_PARENTS
ADVSAFE_THESIS = (
    "Adversary regression after SEMFIX (AS0 ADVSAFE-20 citing AR-ADVREG-01/05) "
    "must keep SEMWRAP false-hit 0; SAFE≠answer-quality — not generative IQ"
)

# Near-miss needles: silent wrong parent golds (same traps as ADVREG family).
FORBIDDEN_NEEDLES: Mapping[str, tuple[str, ...]] = {
    "AS-ADVSAFE-01": ("cs = ent / 32", "cs=ent/32"),
    "AS-ADVSAFE-02": ("0x00000000",),
    "AS-ADVSAFE-03": ("p2wpkh",),
    "AS-ADVSAFE-04": ("append",),
    "AS-ADVSAFE-05": ("pass",),
    "AS-ADVSAFE-06": ("isize", "usize"),
    "AS-ADVSAFE-07": ("secp256k1",),
    "AS-ADVSAFE-08": ("/rest/tx/", "block-hash", "block/<"),
}


def _ids_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    ids = [str(p.get("id", "")).strip() for p in rows]
    if len(set(ids)) != ADVSAFE_N or not all(ids):
        return False
    return all(i.startswith("AS-ADVSAFE-") for i in ids)


def _asks_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    for item in rows:
        if str(item.get("expect", "")) != "no_false_hit":
            return False
        if str(item.get("kind", "")) not in ADV_KINDS:
            return False
        ask = str(item.get("ask", ""))
        tid = str(item.get("id", ""))
        if tid == "AS-ADVSAFE-19":
            if ask.strip():
                return False
        elif not ask.strip():
            return False
    return True


def pack_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AS0 ADVSAFE pack
    WHEN validating ADVSAFE inputs
    THEN True iff N=20, cite 01/05, kinds present, expect=no_false_hit.
    """
    rows = list(pack) if pack is not None else list(ADVSAFE_PACK)
    if len(rows) != ADVSAFE_N or not _ids_ok(rows):
        return False
    if advsafe_missing_required_parents(rows):
        return False
    kinds = advsafe_kind_counts(rows)
    if set(kinds) != ADV_KINDS or any(kinds.get(k, 0) < 1 for k in ADV_KINDS):
        return False
    return _asks_ok(rows)


def classify_advsafe(
    *,
    item: Mapping[str, str],
    looked_up: str | None,
) -> str:
    """
    GIVEN SEMWRAP result on an ADVSAFE ask
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


def score_advsafe_trial(
    *,
    mode: str,
    kind: str,
    outcome: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN ADVSAFE classify outcome
    WHEN scoring
    THEN FALSE_HIT→0; SAFE→9 + SAFE≠quality note (mean not sold as IQ).
    """
    score, err, notes = score_advfp_trial(mode=mode, kind=kind, outcome=outcome)
    notes = list(notes) + [
        SAFE_NOTE,
        "ADVSAFE regression — mean/SAFE is not answer quality / generative IQ",
    ]
    return score, err, notes


def false_hit_ids(trials: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return trial ids classified FALSE_HIT."""
    return [
        str(t.get("trial_id", ""))
        for t in trials
        if str(t.get("outcome", "")) == "FALSE_HIT" and t.get("trial_id")
    ]


def advsafe_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_safe: int,
    n_false_hit: int,
    kind_false: Mapping[str, int],
    parents_cited: Sequence[str],
) -> dict[str, Any]:
    """
    GIVEN 20 ADVSAFE scores
    WHEN summarizing AS3
    THEN false-hit count + SAFE≠quality flag + parent citation + pass.
    """
    if len(scores) != ADVSAFE_N or len(errors) != ADVSAFE_N:
        raise ValueError(f"ADVSAFE requires exactly {ADVSAFE_N} scores/errors")
    mean = float(sum(scores) / float(ADVSAFE_N))
    cited = set(str(p) for p in parents_cited if str(p).strip())
    return {
        "n_trials": ADVSAFE_N,
        "mean": mean,
        "mean_is_quality": False,
        "safe_note": SAFE_NOTE,
        "n_errors": int(sum(1 for e in errors if e)),
        "n_safe": int(n_safe),
        "n_false_hit": int(n_false_hit),
        "false_hit_by_kind": dict(kind_false),
        "pass_false_hit": int(n_false_hit) == 0,
        "required_parents": sorted(REQUIRED_PARENTS),
        "cited_parents": sorted(cited),
        "pass_parents": REQUIRED_PARENTS <= cited,
    }


def decide_advsafe(stats: Mapping[str, Any]) -> str:
    """
    GIVEN ADVSAFE stats
    WHEN applying pesquisa §5 AS3 gate
    THEN PROMOTE iff FH 0 · SAFE≠quality · AR-ADVREG-01/05 cited; else KILL.
    """
    if not bool(stats.get("pass_parents")):
        return "KILL (missing required AR-ADVREG-01/05 citations)"
    if not bool(stats.get("pass_false_hit")):
        return "KILL"
    if bool(stats.get("mean_is_quality")):
        return "KILL (mean sold as answer quality)"
    note = str(stats.get("safe_note", ""))
    if "≠" not in note and "!=" not in note:
        return "KILL (SAFE≠quality note missing)"
    return "PROMOTE"
