"""Wave Z error bank: schema, append, stage pass gate (pesquisa §9.5–9.6)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = [
    "ERROR_REQUIRED",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "validate_error_row",
    "append_error_row",
    "stage_pass",
]

ERROR_REQUIRED = (
    "trial_id",
    "question",
    "source_id",
    "model_raw",
    "score",
    "error",
    "recipe_id",
)
PASS_MEAN = 7.0
PASS_MAX_ERRORS = 3


def validate_error_row(row: Mapping[str, Any]) -> list[str]:
    """
    GIVEN an error-bank row
    WHEN validating schema
    THEN return error strings (empty iff ok).
    """
    errs = [f"missing key: {k}" for k in ERROR_REQUIRED if k not in row]
    if errs:
        return errs
    try:
        s = float(row["score"])  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return ["score must be numeric 0..10"]
    if s < 0.0 or s > 10.0:
        errs.append("score must be in [0, 10]")
    if not isinstance(row.get("error"), bool):
        errs.append("error must be bool")
    return errs


def append_error_row(path: Path, row: Mapping[str, Any]) -> None:
    """Append one validated JSONL row; raise ValueError if schema fails."""
    errs = validate_error_row(row)
    if errs:
        raise ValueError("; ".join(errs))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(row), ensure_ascii=False) + "\n")


def stage_pass(
    *,
    scores: Sequence[float],
    n_errors: int,
) -> dict[str, Any]:
    """
    GIVEN 10 HITL scores + error count
    WHEN checking stage pass bar
    THEN pass iff mean≥7.0 and errors≤3.
    """
    if len(scores) != 10:
        raise ValueError("stage_pass requires exactly 10 scores")
    mean = float(sum(scores) / 10.0)
    ok = mean >= PASS_MEAN and int(n_errors) <= PASS_MAX_ERRORS
    return {
        "ok": ok,
        "mean": mean,
        "n_errors": int(n_errors),
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }
