"""Wave AQ2 H-ADVFP: adversary false-hit suite on SEMWRAP (AQ0 pack)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aq_session_ops import (
    ADV_KINDS,
    AQ0_ADV_N,
    AQ0_ADV_PACK,
    adv_kind_counts,
)

__all__ = [
    "ADVFP_ID",
    "ADVFP_N",
    "ADVFP_PACK",
    "ADVFP_THESIS",
    "FORBIDDEN_NEEDLES",
    "pack_ok",
    "classify_advfp",
    "score_advfp_trial",
    "false_hit_ids",
    "advfp_stats",
    "decide_advfp",
]

ADVFP_ID = "H-ADVFP"
ADVFP_N = AQ0_ADV_N  # 20 — frozen AQ0 adversary pack
ADVFP_PACK = AQ0_ADV_PACK
ADVFP_THESIS = (
    "Adversary / near-miss / OOD / trap suite must keep SEMWRAP false-hit 0 "
    "(no silent wrong gold); product safety — not generative IQ"
)

# Near-miss: needles that mean SEMWRAP returned the trap/wrong parent gold.
FORBIDDEN_NEEDLES: Mapping[str, tuple[str, ...]] = {
    "AQ-ADV-01": ("cs = ent / 32", "cs=ent/32"),
    "AQ-ADV-02": ("0x00000000",),
    "AQ-ADV-03": ("p2wpkh",),  # L=20 wrong; L=32→P2WSH allowed
    "AQ-ADV-04": ("append",),
    "AQ-ADV-05": ("pass",),
    "AQ-ADV-06": ("isize", "usize"),
    "AQ-ADV-07": ("secp256k1",),
    "AQ-ADV-08": ("/rest/tx/", "block-hash", "block/<"),
}


def _ids_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    ids = [str(p.get("id", "")).strip() for p in rows]
    if len(set(ids)) != ADVFP_N or not all(ids):
        return False
    return all(i.startswith("AQ-ADV-") for i in ids)


def _asks_ok(rows: Sequence[Mapping[str, str]]) -> bool:
    for item in rows:
        if str(item.get("expect", "")) != "no_false_hit":
            return False
        if str(item.get("kind", "")) not in ADV_KINDS:
            return False
        ask = str(item.get("ask", ""))
        tid = str(item.get("id", ""))
        if tid == "AQ-ADV-19":
            if ask.strip():
                return False
        elif not ask.strip():
            return False
    return True


def pack_ok(pack: Sequence[Mapping[str, str]] | None = None) -> bool:
    """
    GIVEN AQ0 adversary pack
    WHEN validating ADVFP inputs
    THEN True iff N=20, kinds present, expect=no_false_hit.
    """
    rows = list(pack) if pack is not None else list(ADVFP_PACK)
    if len(rows) != ADVFP_N:
        return False
    if not _ids_ok(rows):
        return False
    kinds = adv_kind_counts(rows)
    if set(kinds) != ADV_KINDS or any(kinds.get(k, 0) < 1 for k in ADV_KINDS):
        return False
    return _asks_ok(rows)


def classify_advfp(
    *,
    item: Mapping[str, str],
    looked_up: str | None,
) -> str:
    """
    GIVEN SEMWRAP result on an adversary ask
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


def score_advfp_trial(
    *,
    mode: str,
    kind: str,
    outcome: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN ADVFP classify outcome
    WHEN scoring
    THEN FALSE_HIT→0 error; SAFE→9 (miss/decode ok — no silent gold).
    """
    if outcome == "FALSE_HIT":
        return (
            0.0,
            True,
            [
                f"FALSE_HIT via {mode}: adversary ask retrieved a bank gold",
                f"kind={kind} — silent wrong gold forbidden",
                "KILL gate if any false-hit remains",
            ],
        )
    return (
        9.0,
        False,
        [
            f"SAFE via {mode}: no bank gold retrieved (kind={kind})",
            "MISS/DECODE ok for adversary — not LOOKUP-as-IQ",
            "expect=no_false_hit satisfied",
        ],
    )


def false_hit_ids(trials: Sequence[Mapping[str, Any]]) -> list[str]:
    """Return trial ids classified FALSE_HIT."""
    return [
        str(t.get("trial_id", ""))
        for t in trials
        if str(t.get("outcome", "")) == "FALSE_HIT" and t.get("trial_id")
    ]


def advfp_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_safe: int,
    n_false_hit: int,
    kind_false: Mapping[str, int],
) -> dict[str, Any]:
    """
    GIVEN 20 ADVFP scores
    WHEN summarizing AQ2
    THEN false-hit count + per-kind breakdown + pass flag.
    """
    if len(scores) != ADVFP_N or len(errors) != ADVFP_N:
        raise ValueError(f"ADVFP requires exactly {ADVFP_N} scores/errors")
    mean = float(sum(scores) / float(ADVFP_N))
    return {
        "n_trials": ADVFP_N,
        "mean": mean,
        "n_errors": int(sum(1 for e in errors if e)),
        "n_safe": int(n_safe),
        "n_false_hit": int(n_false_hit),
        "false_hit_by_kind": dict(kind_false),
        "pass_false_hit": int(n_false_hit) == 0,
    }


def decide_advfp(stats: Mapping[str, Any]) -> str:
    """
    GIVEN ADVFP stats
    WHEN applying pesquisa §5 AQ2 gate
    THEN PROMOTE iff false-hit 0; else KILL (no silent wrong gold).
    """
    if bool(stats.get("pass_false_hit")):
        return "PROMOTE"
    return "KILL"
