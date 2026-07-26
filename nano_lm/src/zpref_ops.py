"""H-ZPREF: preference gold≻raw (DPO-lite rank); story floor + wrap verify."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from lat_ops import EPS_LP

__all__ = [
    "HYPOTHESIS",
    "STAG_TIP_LP",
    "EPS_LP",
    "MIN_BANK_ROWS",
    "MIN_PREF",
    "DEFAULT_STEPS",
    "DEFAULT_REJECTED",
    "BETA",
    "format_qa",
    "bank_pref_pairs",
    "decide_hzpref",
]

HYPOTHESIS = "H-ZPREF"
STAG_TIP_LP = -12.49
MIN_BANK_ROWS = 20
MIN_PREF = 10
DEFAULT_STEPS = 40
DEFAULT_REJECTED = "........"
BETA = 1.0


def format_qa(question: str, answer: str) -> str:
    """Pack Q→A as causal text (chosen or rejected completion)."""
    return f"Q: {str(question).strip()}\nA: {str(answer).strip()}\n"


def bank_pref_pairs(
    rows: Sequence[Mapping[str, Any]],
) -> list[tuple[str, str, str]]:
    """
    GIVEN error_bank rows (bank≥20 after WRAPBANK)
    WHEN building preference fuel
    THEN return (question, chosen=gold, rejected=raw|........) where chosen≠rejected.
    """
    pairs: list[tuple[str, str, str]] = []
    for row in rows:
        gold = row.get("gold") or row.get("repaired")
        q = row.get("question")
        if not q or gold is None:
            continue
        chosen = str(gold).strip()
        if not chosen:
            continue
        raw = str(row.get("model_raw") or "").strip()
        rejected = raw if raw else DEFAULT_REJECTED
        if rejected == chosen:
            continue
        pairs.append((str(q).strip(), chosen, rejected))
    return pairs


def decide_hzpref(
    *,
    story_lp: float,
    n_pairs: int,
    n_bank_rows: int,
    n_params: int,
    parent_story_lp: float,
    wrap_ok: bool,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN preference smoke story_lp + wrap verify
    WHEN gating H-ZPREF (§8.1 AA3)
    THEN PROMOTE iff bank≥20, pairs≥10, params≤5M, story≥parent−ε, wrap_ok.
    """
    if int(n_bank_rows) < MIN_BANK_ROWS:
        return f"KILL (bank rows {n_bank_rows} < {MIN_BANK_ROWS})"
    if int(n_pairs) < MIN_PREF:
        return f"KILL (pref pairs {n_pairs} < {MIN_PREF})"
    if int(n_params) > 5_000_000:
        return "KILL (student >5M)"
    if not bool(wrap_ok):
        return "KILL (Z-HITL wrap verify failed)"
    floor = float(parent_story_lp) - float(eps_lp)
    if float(story_lp) < floor:
        return (
            f"KILL (story_lp {story_lp:.3f} < parent−ε {floor:.3f}; "
            f"parent={parent_story_lp:.3f})"
        )
    return "PROMOTE"
