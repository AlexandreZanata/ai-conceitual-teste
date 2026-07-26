"""H-SERVEALIGN: open-decode ask via QPFB2+BEAMKV (no wrap)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN
from z_z4 import MIN_DELTA_VS_Z1, Z1_MEAN

__all__ = [
    "SERVEALIGN_ID",
    "SERVEALIGN_N",
    "Z1_MEAN",
    "MIN_DELTA_VS_Z1",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "score_open_completion",
    "servealign_stats",
    "decide_servealign",
]

SERVEALIGN_ID = "H-SERVEALIGN"
SERVEALIGN_N = 10


def score_open_completion(completion: str, gold: str) -> tuple[float, bool, list[str]]:
    """
    GIVEN open decode (no wrap) vs curated gold
    WHEN applying Z4-style frontier rubric
    THEN 9 iff exact gold; 1 iff period collapse; else mid error.
    """
    text = str(completion).strip()
    g = str(gold).strip()
    if text and g and text == g:
        return (
            9.0,
            False,
            [
                "open decode matched curated gold",
                "correct and scoped",
                "harm/scope ok",
            ],
        )
    if set(text) <= {".", " "} or text in {"", "........"}:
        return (
            1.0,
            True,
            [
                "completion is only period tokens or empty",
                "incorrect vs gold; fails correctness",
                "in-scope; assertiveness=0",
            ],
        )
    return (
        4.0,
        True,
        [
            "open decode did not match gold",
            "partial or invented content vs curated answer",
            "in-scope; mark error (SERVEALIGN evidence)",
        ],
    )


def servealign_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
) -> dict[str, Any]:
    """
    GIVEN 10 HITL scores + errors (no wrap)
    WHEN summarizing H-SERVEALIGN
    THEN mean, pass_bar, beats_z1.
    """
    if len(scores) != SERVEALIGN_N or len(errors) != SERVEALIGN_N:
        raise ValueError(f"SERVEALIGN requires exactly {SERVEALIGN_N} scores/errors")
    mean = float(sum(scores) / float(SERVEALIGN_N))
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": SERVEALIGN_N,
        "mean": mean,
        "n_errors": n_err,
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "delta_vs_z1": mean - Z1_MEAN,
        "beats_z1": (mean - Z1_MEAN) >= MIN_DELTA_VS_Z1,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "z1_mean": Z1_MEAN,
        "min_delta_vs_z1": MIN_DELTA_VS_Z1,
        "wrap": False,
        "stack": "QPFB2+BEAMKV",
    }


def decide_servealign(stats: Mapping[str, Any]) -> str:
    """
    GIVEN SERVEALIGN stats
    WHEN applying §8.1 AA2 gate
    THEN KILL if not beats Z1+0.5;
         PROMOTE if pass_bar; else HOLD (evidence, not shippable chat).
    """
    if not bool(stats.get("beats_z1")):
        return "KILL"
    if bool(stats.get("pass_bar")):
        return "PROMOTE"
    return "HOLD"
