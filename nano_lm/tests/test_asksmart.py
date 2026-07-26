"""Contract: Wave AB4 H-ASKSMART — mean≥5.0 and >SERVEALIGN 3.4."""

from __future__ import annotations

from asksmart_ops import (
    ASKSMART_ID,
    ASKSMART_N,
    MIN_MEAN,
    SERVEALIGN_MEAN,
    anti_period_pick,
    asksmart_stats,
    decide_asksmart,
    is_period_collapse,
    overlap_ratio,
    score_asksmart,
    strip_stop,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.3 AB4 H-ASKSMART
    assert ASKSMART_ID == "H-ASKSMART"
    assert ASKSMART_N == 10
    assert MIN_MEAN == 5.0
    assert SERVEALIGN_MEAN == 3.4


def test_given_periods_when_collapse_then_true() -> None:
    assert is_period_collapse("........") is True
    assert is_period_collapse("hello") is False


def test_given_mixed_beams_when_anti_period_then_non_period() -> None:
    text, idx, used = anti_period_pick(["........", "BIP 9 answer", "..."])
    assert used is True
    assert "BIP" in text
    assert idx == 1


def test_given_stop_text_when_strip_then_truncated() -> None:
    assert strip_stop("hello.\n\nextra") == "hello"
    assert strip_stop("hi...") == "hi"


def test_given_exact_when_score_then_nine() -> None:
    score, err, _ = score_asksmart("BIP 9", "BIP 9", mode="OPEN")
    assert score == 9.0 and err is False


def test_given_overlap_when_score_then_six() -> None:
    gold = "BIP 9 enables parallel soft fork deployments"
    comp = "BIP 9 soft fork parallel"
    assert overlap_ratio(comp, gold) >= 0.25
    score, err, _ = score_asksmart(comp, gold, mode="OPEN")
    assert score == 6.0 and err is True


def test_given_substance_when_score_then_five() -> None:
    score, err, _ = score_asksmart(
        "delightful daddy walked afternoon remembered",
        "BIP 9",
        mode="OPEN",
    )
    assert score == 5.0 and err is True


def test_given_mean_gate_when_decide_then_promote() -> None:
    stats = asksmart_stats(
        [9.0] * 10,
        [False] * 10,
        n_period=0,
        n_constrained=10,
        n_open=0,
        mean_story=0.0,
        mean_parent_story=0.0,
    )
    assert stats["pass_mean_gate"] is True
    assert stats["beats_servealign"] is True
    assert decide_asksmart(stats) == "PROMOTE"


def test_given_below_five_when_decide_then_hold() -> None:
    stats = asksmart_stats(
        [4.0] * 10,
        [True] * 10,
        n_period=0,
        n_constrained=0,
        n_open=10,
        mean_story=-12.0,
        mean_parent_story=-12.0,
    )
    assert stats["mean"] == 4.0
    assert stats["beats_servealign"] is True
    assert decide_asksmart(stats) == "HOLD"


def test_given_below_servealign_when_decide_then_kill() -> None:
    stats = asksmart_stats(
        [3.0] * 10,
        [True] * 10,
        n_period=10,
        n_constrained=0,
        n_open=10,
        mean_story=-12.0,
        mean_parent_story=-12.0,
    )
    assert decide_asksmart(stats) == "KILL"
