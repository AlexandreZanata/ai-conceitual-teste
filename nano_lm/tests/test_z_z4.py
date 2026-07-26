"""Contract: Wave Z4 three-arm HITL gate + claim branch."""

from __future__ import annotations

from z_z4 import (
    ARM_SPECS,
    MIN_DELTA_VS_Z1,
    PASS_MAX_ERRORS,
    PASS_MEAN,
    Z1_MEAN,
    arm_stats,
    claim_branch,
    decide_z4,
)


def test_given_ten_high_scores_when_arm_stats_then_pass_bar() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9.5 pass bar mean≥7 errors≤3
    s = arm_stats([9.0] * 10, [False] * 10)
    assert s["mean"] == 9.0
    assert s["n_errors"] == 0
    assert s["pass_bar"] is True
    assert s["beats_z1"] is True
    assert s["delta_vs_z1"] == 9.0 - Z1_MEAN


def test_given_z1_like_when_arm_stats_then_fail_bar() -> None:
    s = arm_stats([1.0] * 10, [True] * 10)
    assert s["pass_bar"] is False
    assert s["beats_z1"] is False
    assert s["n_errors"] == 10


def test_given_arm_a_pass_when_decide_then_pass() -> None:
    a = arm_stats([9.0] * 10, [False] * 10)
    assert decide_z4(a) == "PASS"


def test_given_arm_a_fail_when_decide_then_fail() -> None:
    a = arm_stats([1.0] * 10, [True] * 10)
    assert decide_z4(a) == "FAIL"


def test_given_wrap_ok_raw_fail_when_claim_then_hzwrap() -> None:
    # §8 #2: PASS only with lookup → H-ZWRAP product path
    a = arm_stats([9.0] * 10, [False] * 10)
    b = arm_stats([9.0] * 10, [False] * 10)
    c = arm_stats([1.0] * 10, [True] * 10)
    assert claim_branch(a, b, c) == "H-ZWRAP"


def test_given_arm_a_fail_when_claim_then_fail() -> None:
    a = arm_stats([1.0] * 10, [True] * 10)
    b = arm_stats([9.0] * 10, [False] * 10)
    c = arm_stats([1.0] * 10, [True] * 10)
    assert claim_branch(a, b, c) == "FAIL"


def test_given_raw_pass_when_claim_then_mixed() -> None:
    a = arm_stats([9.0] * 10, [False] * 10)
    b = arm_stats([9.0] * 10, [False] * 10)
    c = arm_stats([8.0] * 10, [False] * 10)
    assert claim_branch(a, b, c) == "MIXED"


def test_given_constants_when_loaded_then_match_pesquisa() -> None:
    assert PASS_MEAN == 7.0
    assert PASS_MAX_ERRORS == 3
    assert Z1_MEAN == 1.0
    assert MIN_DELTA_VS_Z1 == 0.5
    assert set(ARM_SPECS) == {"A", "B", "C"}
    assert ARM_SPECS["A"][1] is True
    assert ARM_SPECS["C"][1] is False
