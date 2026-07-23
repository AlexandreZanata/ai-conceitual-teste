"""Holdout helpers for H-HOLD: disjoint fit/eval prompts + overfit flag."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

# Smoke ε: train_fit − eval_lp above this ⇒ overfit kill (integrity).
OVERFIT_GAP = 1.0


def load_prompt_ids(path: Path) -> list[str]:
    """
    GIVEN a prompts YAML with id fields
    WHEN loading ids
    THEN return ordered non-empty id strings.
    """
    with path.open(encoding="utf-8") as f:
        prompts = yaml.safe_load(f)["prompts"]
    ids = [str(p["id"]) for p in prompts]
    if not ids or any(not i for i in ids):
        raise ValueError("load_prompt_ids: empty or blank id")
    return ids


def assert_disjoint(fit_ids: Sequence[str], eval_ids: Sequence[str]) -> None:
    """
    GIVEN fit and eval prompt id lists
    WHEN validating holdout integrity
    THEN raise if any shared id (fitness/eval leak).
    """
    overlap = sorted(set(fit_ids) & set(eval_ids))
    if overlap:
        raise ValueError(f"assert_disjoint: overlap {overlap}")


def overfit_gap(train_fit: float, eval_lp: float) -> float:
    """train_fit − eval_lp (positive ⇒ train looks better than eval)."""
    return float(train_fit) - float(eval_lp)


def is_overfit(
    train_fit: float, eval_lp: float, *, threshold: float = OVERFIT_GAP
) -> bool:
    """True when train_fit exceeds eval_lp by more than threshold."""
    if threshold <= 0.0:
        raise ValueError("is_overfit: threshold must be > 0")
    return overfit_gap(train_fit, eval_lp) > threshold


def decide_hhold(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-HOLD family stats (may include overfit flag)
    WHEN deciding promote/kill
    THEN KILL on overfit; else require beat B2 on eval teacher_lp.
    """
    if float(s.get("overfit", 0.0)) > 0.0:
        return "KILL (overfit train≫eval)"
    b2 = stats.get("B2", {}).get("mean_lp")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2) + 1e-6:
        return "PROMOTE (beats B2, holdout ok)"
    return "KILL / hold (≤ B2)"


def attach_overfit(
    row: dict[str, Any], train_fit: float, *, threshold: float = OVERFIT_GAP
) -> dict[str, Any]:
    """Annotate eval row with train_fit, gap, and overfit bool."""
    eval_lp = float(row["teacher_mean_logprob"])
    gap = overfit_gap(train_fit, eval_lp)
    row["train_fit"] = float(train_fit)
    row["overfit_gap"] = gap
    row["overfit"] = is_overfit(train_fit, eval_lp, threshold=threshold)
    return row
