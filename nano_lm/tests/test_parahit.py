"""Contract: Wave AQ1 H-PARAHIT — paraphrase SEMWRAP hit-rate (pesquisa §5)."""

from __future__ import annotations

from parahit_ops import (
    MIN_HIT_RATE,
    MIN_MEAN,
    PARAHIT_ID,
    PARAHIT_N,
    PARAHIT_PACK,
    PARAHIT_THESIS,
    decide_parahit,
    miss_ids,
    pack_ok,
    parahit_stats,
    score_parahit_trial,
)


def test_given_contract_when_constants_then_match_aq0_pack() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ1 — hit≥bar · false-hit 0 · report misses
    assert PARAHIT_ID == "H-PARAHIT"
    assert PARAHIT_N == 20
    assert MIN_HIT_RATE == 0.70
    assert MIN_MEAN == 7.0
    assert len(PARAHIT_PACK) == 20
    assert pack_ok() is True
    assert "PARAHIT" in PARAHIT_THESIS or "paraphrase" in PARAHIT_THESIS


def test_given_pack_when_ids_then_aq_para_prefix() -> None:
    for item in PARAHIT_PACK:
        assert item["id"].startswith("AQ-PARA-")
        assert item["paraphrase"].strip()
        assert item["parent_question"].strip()
        assert item["gold"].strip()


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_parahit_trial(
        mode="SEMWRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
    )
    assert score == 9.0
    assert err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_false_hit_when_score_then_zero_error() -> None:
    score, err, _notes = score_parahit_trial(
        mode="SEMWRAP_LOOKUP",
        completion="wrong gold",
        expected_gold="CS = ENT / 32",
        lookup_kind="FALSE_HIT",
    )
    assert score == 0.0
    assert err is True


def test_given_stats_when_hit_bar_then_promote() -> None:
    scores = [9.0] * 14 + [4.0] * 6
    errors = [False] * 14 + [True] * 6
    stats = parahit_stats(
        scores,
        errors,
        n_true_hit=14,
        n_false_hit=0,
        n_miss=6,
    )
    assert stats["hit_rate"] == 0.7
    assert stats["pass_hit_rate"] is True
    assert stats["pass_false_hit"] is True
    # mean = (14*9 + 6*4)/20 = 7.5
    assert decide_parahit(stats) == "PROMOTE"


def test_given_stats_when_low_hit_then_hold() -> None:
    scores = [9.0] * 10 + [4.0] * 10
    errors = [False] * 10 + [True] * 10
    stats = parahit_stats(
        scores,
        errors,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=10,
    )
    assert stats["pass_hit_rate"] is False
    assert decide_parahit(stats) == "HOLD"


def test_given_stats_when_false_hit_then_kill() -> None:
    scores = [9.0] * 19 + [0.0]
    errors = [False] * 19 + [True]
    stats = parahit_stats(
        scores,
        errors,
        n_true_hit=19,
        n_false_hit=1,
        n_miss=0,
    )
    assert decide_parahit(stats) == "KILL"


def test_given_trials_when_miss_ids_then_listed() -> None:
    trials = [
        {"trial_id": "AQ-PARA-01", "lookup_kind": "TRUE_HIT"},
        {"trial_id": "AQ-PARA-02", "lookup_kind": "MISS"},
        {"trial_id": "AQ-PARA-03", "lookup_kind": "FALSE_HIT"},
    ]
    assert miss_ids(trials) == ["AQ-PARA-02", "AQ-PARA-03"]
