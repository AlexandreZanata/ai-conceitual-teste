"""Contract: Wave AS4 H-PARAEXT2 — external paraphrase after SEMFIX."""

from __future__ import annotations

from paraext2_ops import (
    MIN_HIT_RATE,
    MIN_MEAN,
    PARAEXT2_ID,
    PARAEXT2_N,
    PARAEXT2_PACK,
    PARAEXT2_THESIS,
    decide_paraext2,
    miss_ids,
    pack_ok,
    paraext2_stats,
    score_paraext2_trial,
)


def test_given_contract_when_constants_then_match_as4() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS4 — hit≥0.70 · FH 0 · misses listed
    assert PARAEXT2_ID == "H-PARAEXT2"
    assert PARAEXT2_N == 20
    assert MIN_HIT_RATE == 0.70
    assert MIN_MEAN == 7.0
    assert len(PARAEXT2_PACK) == 20
    assert pack_ok() is True
    assert "PARAEXT2" in PARAEXT2_THESIS or "SEMFIX" in PARAEXT2_THESIS


def test_given_pack_when_ids_then_as_ext2_prefix() -> None:
    for item in PARAEXT2_PACK:
        assert item["id"].startswith("AS-EXT2-")
        assert item["paraphrase"].strip()
        assert item["parent_question"].strip()
        assert item["gold"].strip()


def test_given_copied_aq_para_when_pack_ok_then_false() -> None:
    from aq_session_ops import AQ0_PARA_PACK

    bad = [dict(p) for p in PARAEXT2_PACK]
    bad[0]["paraphrase"] = AQ0_PARA_PACK[0]["paraphrase"]
    assert pack_ok(bad) is False


def test_given_copied_ar_ext_when_pack_ok_then_false() -> None:
    from ar_session_ops import AR0_EXT_PARA_PACK

    bad = [dict(p) for p in PARAEXT2_PACK]
    bad[0]["paraphrase"] = AR0_EXT_PARA_PACK[0]["paraphrase"]
    assert pack_ok(bad) is False


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_paraext2_trial(
        mode="SEMWRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
    )
    assert score == 9.0
    assert err is False
    assert any("not generative IQ" in n for n in notes)
    assert any("PARAEXT2" in n for n in notes)


def test_given_false_hit_when_score_then_zero_error() -> None:
    score, err, _notes = score_paraext2_trial(
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
    stats = paraext2_stats(
        scores,
        errors,
        n_true_hit=14,
        n_false_hit=0,
        n_miss=6,
    )
    assert stats["hit_rate"] == 0.7
    assert decide_paraext2(stats) == "PROMOTE"


def test_given_stats_when_low_hit_then_hold() -> None:
    scores = [9.0] * 10 + [4.0] * 10
    errors = [False] * 10 + [True] * 10
    stats = paraext2_stats(
        scores,
        errors,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=10,
    )
    assert decide_paraext2(stats) == "HOLD"


def test_given_stats_when_false_hit_then_kill() -> None:
    scores = [9.0] * 19 + [0.0]
    errors = [False] * 19 + [True]
    stats = paraext2_stats(
        scores,
        errors,
        n_true_hit=19,
        n_false_hit=1,
        n_miss=0,
    )
    assert decide_paraext2(stats) == "KILL"


def test_given_trials_when_miss_ids_then_listed() -> None:
    trials = [
        {"trial_id": "AS-EXT2-01", "lookup_kind": "TRUE_HIT"},
        {"trial_id": "AS-EXT2-02", "lookup_kind": "MISS"},
        {"trial_id": "AS-EXT2-07", "lookup_kind": "FALSE_HIT"},
    ]
    assert miss_ids(trials) == ["AS-EXT2-02", "AS-EXT2-07"]
