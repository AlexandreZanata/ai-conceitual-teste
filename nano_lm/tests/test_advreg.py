"""Contract: Wave AR4 H-ADVREG — adversary regression + SAFE≠quality."""

from __future__ import annotations

from advreg_ops import (
    ADVREG_ID,
    ADVREG_N,
    ADVREG_PACK,
    ADVREG_THESIS,
    SAFE_NOTE,
    advreg_stats,
    classify_advreg,
    decide_advreg,
    false_hit_ids,
    pack_ok,
    score_advreg_trial,
)


def test_given_contract_when_constants_then_match_ar0_pack() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR4 — FH 0 · SAFE≠quality · ≠ AQ-ADV
    assert ADVREG_ID == "H-ADVREG"
    assert ADVREG_N == 20
    assert len(ADVREG_PACK) == 20
    assert pack_ok() is True
    assert "≠" in SAFE_NOTE
    assert "false-hit" in ADVREG_THESIS or "ADVREG" in ADVREG_THESIS


def test_given_pack_when_ids_then_ar_advreg_prefix() -> None:
    kinds = {p["kind"] for p in ADVREG_PACK}
    assert kinds == {"near-miss", "ood", "trap"}
    for item in ADVREG_PACK:
        assert item["id"].startswith("AR-ADVREG-")
        assert item["expect"] == "no_false_hit"


def test_given_copied_aq_ask_when_pack_ok_then_false() -> None:
    from aq_session_ops import AQ0_ADV_PACK

    bad = [dict(p) for p in ADVREG_PACK]
    bad[0]["ask"] = AQ0_ADV_PACK[0]["ask"]
    assert pack_ok(bad) is False


def test_given_lookup_gold_when_classify_then_false_hit() -> None:
    item = {"id": "AR-ADVREG-01", "kind": "near-miss"}
    assert (
        classify_advreg(item=item, looked_up="CS = ENT / 32") == "FALSE_HIT"
    )
    ood = {"id": "AR-ADVREG-09", "kind": "ood"}
    assert classify_advreg(item=ood, looked_up="any bank gold") == "FALSE_HIT"


def test_given_decode_miss_when_classify_then_safe() -> None:
    item = {"id": "AR-ADVREG-01", "kind": "near-miss"}
    assert classify_advreg(item=item, looked_up=None) == "SAFE"


def test_given_safe_when_score_then_nine_with_safe_note() -> None:
    score, err, notes = score_advreg_trial(
        mode="WRAP_DECODE", kind="ood", outcome="SAFE"
    )
    assert score == 9.0
    assert err is False
    assert any("≠" in n or "not answer quality" in n for n in notes)


def test_given_false_hit_when_score_then_zero() -> None:
    score, err, notes = score_advreg_trial(
        mode="SEMWRAP_LOOKUP", kind="near-miss", outcome="FALSE_HIT"
    )
    assert score == 0.0
    assert err is True
    assert any("FALSE_HIT" in n for n in notes)


def test_given_stats_when_zero_false_then_promote() -> None:
    scores = [9.0] * 20
    errors = [False] * 20
    stats = advreg_stats(
        scores,
        errors,
        n_safe=20,
        n_false_hit=0,
        kind_false={"near-miss": 0, "ood": 0, "trap": 0},
    )
    assert stats["mean_is_quality"] is False
    assert decide_advreg(stats) == "PROMOTE"


def test_given_stats_when_any_false_then_kill() -> None:
    scores = [9.0] * 19 + [0.0]
    errors = [False] * 19 + [True]
    stats = advreg_stats(
        scores,
        errors,
        n_safe=19,
        n_false_hit=1,
        kind_false={"near-miss": 1, "ood": 0, "trap": 0},
    )
    assert decide_advreg(stats) == "KILL"
    trials = [
        {"trial_id": "AR-ADVREG-01", "outcome": "SAFE"},
        {"trial_id": "AR-ADVREG-02", "outcome": "FALSE_HIT"},
    ]
    assert false_hit_ids(trials) == ["AR-ADVREG-02"]


def test_given_mean_as_quality_when_decide_then_kill() -> None:
    scores = [9.0] * 20
    errors = [False] * 20
    stats = advreg_stats(
        scores,
        errors,
        n_safe=20,
        n_false_hit=0,
        kind_false={"near-miss": 0, "ood": 0, "trap": 0},
    )
    stats["mean_is_quality"] = True
    assert decide_advreg(stats).startswith("KILL")
