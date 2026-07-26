"""Wave Z4 HITL-10 verify: three-arm gate (zerr+wrap / wrap-only / zerr-raw)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "Z1_MEAN",
    "MIN_DELTA_VS_Z1",
    "ARM_SPECS",
    "arm_stats",
    "decide_z4",
    "claim_branch",
]

PASS_MEAN = 7.0
PASS_MAX_ERRORS = 3
Z1_MEAN = 1.0
MIN_DELTA_VS_Z1 = 0.5

# arm_id → (label, wrap, root_key)
ARM_SPECS: dict[str, tuple[str, bool, str]] = {
    "A": ("zerr+wrap", True, "zerr"),
    "B": ("wrap-only", True, "champion"),
    "C": ("zerr-raw", False, "zerr"),
}


def arm_stats(scores: Sequence[float], errors: Sequence[bool]) -> dict[str, Any]:
    """
    GIVEN 10 trial scores + error flags
    WHEN summarizing one Z4 arm
    THEN return mean, n_errors, and pass-bar flags.
    """
    if len(scores) != 10 or len(errors) != 10:
        raise ValueError("each arm requires exactly 10 scores and 10 errors")
    mean = float(sum(scores) / 10.0)
    n_err = int(sum(1 for e in errors if e))
    return {
        "n_trials": 10,
        "mean": mean,
        "n_errors": n_err,
        "pass_bar": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "delta_vs_z1": mean - Z1_MEAN,
        "beats_z1": (mean - Z1_MEAN) >= MIN_DELTA_VS_Z1,
    }


def decide_z4(arm_a: Mapping[str, Any]) -> str:
    """
    GIVEN primary arm A stats
    WHEN applying Z4 verify gate
    THEN PASS iff pass_bar and beats_z1; else FAIL.
    """
    if bool(arm_a.get("pass_bar")) and bool(arm_a.get("beats_z1")):
        return "PASS"
    return "FAIL"


def claim_branch(
    arm_a: Mapping[str, Any],
    arm_b: Mapping[str, Any],
    arm_c: Mapping[str, Any],
) -> str:
    """
    GIVEN three arm stats after Z4
    WHEN branching product claims (§8 #2 vs #3)
    THEN return H-ZWRAP | H-SERVEALIGN | MIXED | FAIL.
    """
    a_ok = bool(arm_a.get("pass_bar"))
    b_ok = bool(arm_b.get("pass_bar"))
    c_ok = bool(arm_c.get("pass_bar"))
    if not a_ok:
        return "FAIL"
    if a_ok and b_ok and not c_ok:
        return "H-ZWRAP"
    if a_ok and not c_ok:
        return "H-SERVEALIGN"
    if c_ok:
        return "MIXED"
    return "FAIL"
