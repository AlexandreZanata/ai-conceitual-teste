"""Wave Z trial JSON schema (Z1 prep) + validate."""

from __future__ import annotations

from typing import Any, Mapping

__all__ = ["TRIAL_REQUIRED", "validate_trial"]

TRIAL_REQUIRED = (
    "trial_id",
    "stage",
    "question",
    "source_id",
    "recipe_id",
    "completion",
    "score",
    "error",
)


def validate_trial(trial: Mapping[str, Any]) -> list[str]:
    """
    GIVEN a HITL trial dict
    WHEN validating schema
    THEN return error strings (empty iff ok).
    """
    errs: list[str] = []
    for key in TRIAL_REQUIRED:
        if key not in trial:
            errs.append(f"missing key: {key}")
    if errs:
        return errs
    score = trial.get("score")
    try:
        s = float(score)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return ["score must be numeric 0..10"]
    if s < 0.0 or s > 10.0:
        errs.append("score must be in [0, 10]")
    if not isinstance(trial.get("error"), bool):
        errs.append("error must be bool")
    tid = str(trial.get("trial_id", ""))
    # Wave Z + AA…AR letter packs (Z1-01 · AQ-PARA-01 · AR-EXT-01 · …)
    allowed = (
        "Z",
        "AA",
        "AB",
        "AC",
        "AD",
        "AE",
        "AF",
        "AG",
        "AH",
        "AI",
        "AJ",
        "AK",
        "AL",
        "AM",
        "AN",
        "AO",
        "AP",
        "AQ",
        "AR",
    )
    if not any(tid.startswith(p) for p in allowed):
        errs.append(
            "trial_id must start with Z* / AA*…AR* wave prefix"
        )
    return errs
