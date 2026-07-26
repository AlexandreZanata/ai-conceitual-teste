"""H-ZERR: supervised CE on Wave Z error-bank (question→gold); parent floor."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from lat_ops import EPS_LP

__all__ = [
    "HYPOTHESIS",
    "STAG_TIP_LP",
    "EPS_LP",
    "MIN_BANK",
    "DEFAULT_STEPS",
    "format_qa",
    "bank_qa_pairs",
    "decide_hzerr",
]

HYPOTHESIS = "H-ZERR"
STAG_TIP_LP = -12.49  # tip scoreboard reference (not Z0 B2 floor)
MIN_BANK = 10
DEFAULT_STEPS = 40


def format_qa(question: str, gold: str) -> str:
    """Pack one supervised pair as causal text (no MIXD)."""
    return f"Q: {str(question).strip()}\nA: {str(gold).strip()}\n"


def bank_qa_pairs(rows: Sequence[Mapping[str, Any]]) -> list[tuple[str, str]]:
    """
    GIVEN error_bank rows
    WHEN extracting retrain fuel
    THEN return (question, gold) for error/score<8 rows with gold text.
    """
    pairs: list[tuple[str, str]] = []
    for row in rows:
        if not (bool(row.get("error")) or float(row.get("score", 10)) < 8.0):
            continue
        gold = row.get("gold") or row.get("repaired")
        q = row.get("question")
        if not q or gold is None:
            continue
        g = str(gold).strip()
        if not g:
            continue
        pairs.append((str(q).strip(), g))
    return pairs


def decide_hzerr(
    *,
    story_lp: float,
    n_pairs: int,
    n_params: int,
    parent_story_lp: float,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN smoke story_lp after bank CE
    WHEN gating H-ZERR vs exported champion parent
    THEN PROMOTE iff pairs≥10, params≤5M, story_lp ≥ parent−ε
    (Z0 B2 may sit below tip STAG′; do not use absolute tip floor).
    """
    if int(n_pairs) < MIN_BANK:
        return f"KILL (bank pairs {n_pairs} < {MIN_BANK})"
    if int(n_params) > 5_000_000:
        return "KILL (student >5M)"
    floor = float(parent_story_lp) - float(eps_lp)
    if float(story_lp) < floor:
        return (
            f"KILL (story_lp {story_lp:.3f} < parent−ε {floor:.3f}; "
            f"parent={parent_story_lp:.3f})"
        )
    return "PROMOTE"
