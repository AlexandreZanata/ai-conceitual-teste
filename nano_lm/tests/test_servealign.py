"""Contract: Wave AA2 H-SERVEALIGN — QPFB2+BEAMKV open decode vs Z1+0.5."""

from __future__ import annotations

from servealign_ops import (
    MIN_DELTA_VS_Z1,
    PASS_MAX_ERRORS,
    PASS_MEAN,
    SERVEALIGN_ID,
    SERVEALIGN_N,
    Z1_MEAN,
    decide_servealign,
    score_open_completion,
    servealign_stats,
)


def test_given_id_when_loaded_then_servealign() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.1 AA2 — open decode QPFB2+BEAMKV
    assert SERVEALIGN_ID == "H-SERVEALIGN"
    assert SERVEALIGN_N == 10
    assert Z1_MEAN == 1.0
    assert MIN_DELTA_VS_Z1 == 0.5
    assert PASS_MEAN == 7.0
    assert PASS_MAX_ERRORS == 3


def test_given_period_when_score_then_error_low() -> None:
    score, err, _ = score_open_completion("........", "def add(a,b): return a+b")
    assert score == 1.0
    assert err is True


def test_given_exact_gold_when_score_then_nine() -> None:
    g = "def add(a, b):\n    return a + b"
    score, err, _ = score_open_completion(g, g)
    assert score == 9.0
    assert err is False


def test_given_partial_when_score_then_mid_error() -> None:
    score, err, _ = score_open_completion("something else entirely", "gold answer")
    assert score == 4.0
    assert err is True


def test_given_high_when_stats_then_pass_bar() -> None:
    s = servealign_stats([9.0] * 10, [False] * 10)
    assert s["pass_bar"] is True
    assert s["beats_z1"] is True
    assert decide_servealign(s) == "PROMOTE"


def test_given_z1_like_when_decide_then_kill() -> None:
    s = servealign_stats([1.0] * 10, [True] * 10)
    assert s["beats_z1"] is False
    assert decide_servealign(s) == "KILL"


def test_given_beats_z1_not_pass_when_decide_then_hold() -> None:
    # mean 4.0 ≥ 1.5 but fails product pass bar
    s = servealign_stats([4.0] * 10, [True] * 10)
    assert s["beats_z1"] is True
    assert s["pass_bar"] is False
    assert decide_servealign(s) == "HOLD"
