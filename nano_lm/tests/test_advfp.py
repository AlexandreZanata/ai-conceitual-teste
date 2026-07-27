"""Contract: Wave AQ2 H-ADVFP — adversary false-hit 0 (pesquisa §5)."""

from __future__ import annotations

from advfp_ops import (
    ADVFP_ID,
    ADVFP_N,
    ADVFP_PACK,
    ADVFP_THESIS,
    advfp_stats,
    classify_advfp,
    decide_advfp,
    false_hit_ids,
    pack_ok,
    score_advfp_trial,
)


def test_given_contract_when_constants_then_match_aq0_pack() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ2 — false-hit 0 · no silent wrong gold
    assert ADVFP_ID == "H-ADVFP"
    assert ADVFP_N == 20
    assert len(ADVFP_PACK) == 20
    assert pack_ok() is True
    assert "false-hit" in ADVFP_THESIS


def test_given_pack_when_kinds_then_near_ood_trap() -> None:
    kinds = {p["kind"] for p in ADVFP_PACK}
    assert kinds == {"near-miss", "ood", "trap"}
    for item in ADVFP_PACK:
        assert item["id"].startswith("AQ-ADV-")
        assert item["expect"] == "no_false_hit"


def test_given_lookup_gold_when_classify_then_false_hit() -> None:
    item = {"id": "AQ-ADV-01", "kind": "near-miss"}
    assert (
        classify_advfp(item=item, looked_up="CS = ENT / 32") == "FALSE_HIT"
    )
    ood = {"id": "AQ-ADV-09", "kind": "ood"}
    assert classify_advfp(item=ood, looked_up="any bank gold") == "FALSE_HIT"


def test_given_decode_miss_when_classify_then_safe() -> None:
    item = {"id": "AQ-ADV-01", "kind": "near-miss"}
    assert classify_advfp(item=item, looked_up=None) == "SAFE"
    # L=32→P2WSH is correct adjacent gold, not the L=20 trap
    adv03 = {"id": "AQ-ADV-03", "kind": "near-miss"}
    assert classify_advfp(item=adv03, looked_up="P2WSH") == "SAFE"


def test_given_false_hit_when_score_then_zero() -> None:
    score, err, notes = score_advfp_trial(
        mode="SEMWRAP_LOOKUP", kind="near-miss", outcome="FALSE_HIT"
    )
    assert score == 0.0
    assert err is True
    assert any("FALSE_HIT" in n for n in notes)


def test_given_safe_when_score_then_nine() -> None:
    score, err, _notes = score_advfp_trial(
        mode="WRAP_DECODE", kind="ood", outcome="SAFE"
    )
    assert score == 9.0
    assert err is False


def test_given_stats_when_zero_false_then_promote() -> None:
    scores = [9.0] * 20
    errors = [False] * 20
    stats = advfp_stats(
        scores,
        errors,
        n_safe=20,
        n_false_hit=0,
        kind_false={"near-miss": 0, "ood": 0, "trap": 0},
    )
    assert stats["pass_false_hit"] is True
    assert decide_advfp(stats) == "PROMOTE"


def test_given_stats_when_any_false_then_kill() -> None:
    scores = [9.0] * 19 + [0.0]
    errors = [False] * 19 + [True]
    stats = advfp_stats(
        scores,
        errors,
        n_safe=19,
        n_false_hit=1,
        kind_false={"near-miss": 1, "ood": 0, "trap": 0},
    )
    assert decide_advfp(stats) == "KILL"
    trials = [
        {"trial_id": "AQ-ADV-01", "outcome": "SAFE"},
        {"trial_id": "AQ-ADV-02", "outcome": "FALSE_HIT"},
    ]
    assert false_hit_ids(trials) == ["AQ-ADV-02"]
