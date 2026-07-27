"""Contract: Wave AS3 H-ADVSAFE — adversary regression after SEMFIX."""

from __future__ import annotations

from advsafe_ops import (
    ADVSAFE_ID,
    ADVSAFE_N,
    ADVSAFE_PACK,
    ADVSAFE_THESIS,
    REQUIRED_PARENTS,
    SAFE_NOTE,
    advsafe_stats,
    classify_advsafe,
    decide_advsafe,
    false_hit_ids,
    pack_ok,
    score_advsafe_trial,
)
from semwrap_ops import contrastive_reject, semantic_lookup


def test_given_contract_when_constants_then_match_as3() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS3 — FH 0 · SAFE≠quality · cite 01/05
    assert ADVSAFE_ID == "H-ADVSAFE"
    assert ADVSAFE_N == 20
    assert len(ADVSAFE_PACK) == 20
    assert pack_ok() is True
    assert REQUIRED_PARENTS == {"AR-ADVREG-01", "AR-ADVREG-05"}
    assert "≠" in SAFE_NOTE
    assert "false-hit" in ADVSAFE_THESIS or "ADVSAFE" in ADVSAFE_THESIS


def test_given_pack_when_ids_then_as_advsafe_prefix() -> None:
    kinds = {p["kind"] for p in ADVSAFE_PACK}
    assert kinds == {"near-miss", "ood", "trap"}
    parents = {str(p.get("parent_id", "")) for p in ADVSAFE_PACK}
    assert REQUIRED_PARENTS <= parents
    for item in ADVSAFE_PACK:
        assert item["id"].startswith("AS-ADVSAFE-")
        assert item["expect"] == "no_false_hit"


def test_given_missing_parent_when_pack_ok_then_false() -> None:
    bad = [dict(p) for p in ADVSAFE_PACK]
    for row in bad:
        if row.get("parent_id") == "AR-ADVREG-01":
            row.pop("parent_id")
    assert pack_ok(bad) is False


def test_given_lookup_gold_when_classify_then_false_hit() -> None:
    item = {"id": "AS-ADVSAFE-01", "kind": "near-miss"}
    assert (
        classify_advsafe(item=item, looked_up="CS = ENT / 32") == "FALSE_HIT"
    )
    ood = {"id": "AS-ADVSAFE-09", "kind": "ood"}
    assert classify_advsafe(item=ood, looked_up="any bank gold") == "FALSE_HIT"


def test_given_decode_miss_when_classify_then_safe() -> None:
    item = {"id": "AS-ADVSAFE-01", "kind": "near-miss"}
    assert classify_advsafe(item=item, looked_up=None) == "SAFE"


def test_given_rest_fee_when_contrast_then_reject() -> None:
    ask = next(p for p in ADVSAFE_PACK if p["id"] == "AS-ADVSAFE-08")["ask"]
    assert contrastive_reject(
        ask,
        "Core REST: GET path for a tx hash with bin|hex|json suffixes?",
        "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
    )


def test_given_bank_when_lookup_01_05_08_then_no_wrong_gold() -> None:
    rows = [
        {
            "question": (
                "BIP-39: what is the formula for checksum length CS in "
                "terms of ENT? (write CS = …)"
            ),
            "source_id": "bip-0039",
            "gold": "CS = ENT / 32",
        },
        {
            "question": (
                "Which keyword is a no-op placeholder statement in Python "
                "(Pass Statements)?"
            ),
            "source_id": "python-tutorial-control",
            "gold": "pass",
        },
        {
            "question": (
                "Core REST: GET path for a tx hash with bin|hex|json suffixes?"
            ),
            "source_id": "bitcoin-rest",
            "gold": "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
        },
    ]
    for tid in ("AS-ADVSAFE-01", "AS-ADVSAFE-05", "AS-ADVSAFE-08"):
        item = next(p for p in ADVSAFE_PACK if p["id"] == tid)
        gold, meta = semantic_lookup(item["ask"], rows)
        assert gold is None
        assert meta["kind"] == "REJECT_NEAR_MISS"
        assert classify_advsafe(item=item, looked_up=gold) == "SAFE"


def test_given_safe_when_score_then_nine_with_safe_note() -> None:
    score, err, notes = score_advsafe_trial(
        mode="WRAP_DECODE", kind="ood", outcome="SAFE"
    )
    assert score == 9.0
    assert err is False
    assert any("≠" in n or "not answer quality" in n for n in notes)


def test_given_false_hit_when_score_then_zero() -> None:
    score, err, notes = score_advsafe_trial(
        mode="SEMWRAP_LOOKUP", kind="near-miss", outcome="FALSE_HIT"
    )
    assert score == 0.0
    assert err is True
    assert any("FALSE_HIT" in n for n in notes)


def test_given_stats_when_zero_false_then_promote() -> None:
    scores = [9.0] * 20
    errors = [False] * 20
    stats = advsafe_stats(
        scores,
        errors,
        n_safe=20,
        n_false_hit=0,
        kind_false={"near-miss": 0, "ood": 0, "trap": 0},
        parents_cited=["AR-ADVREG-01", "AR-ADVREG-05"],
    )
    assert stats["mean_is_quality"] is False
    assert decide_advsafe(stats) == "PROMOTE"


def test_given_stats_when_any_false_then_kill() -> None:
    scores = [9.0] * 19 + [0.0]
    errors = [False] * 19 + [True]
    stats = advsafe_stats(
        scores,
        errors,
        n_safe=19,
        n_false_hit=1,
        kind_false={"near-miss": 1, "ood": 0, "trap": 0},
        parents_cited=["AR-ADVREG-01", "AR-ADVREG-05"],
    )
    assert decide_advsafe(stats) == "KILL"
    trials = [
        {"trial_id": "AS-ADVSAFE-01", "outcome": "SAFE"},
        {"trial_id": "AS-ADVSAFE-08", "outcome": "FALSE_HIT"},
    ]
    assert false_hit_ids(trials) == ["AS-ADVSAFE-08"]


def test_given_mean_as_quality_when_decide_then_kill() -> None:
    scores = [9.0] * 20
    errors = [False] * 20
    stats = advsafe_stats(
        scores,
        errors,
        n_safe=20,
        n_false_hit=0,
        kind_false={"near-miss": 0, "ood": 0, "trap": 0},
        parents_cited=["AR-ADVREG-01", "AR-ADVREG-05"],
    )
    stats["mean_is_quality"] = True
    assert decide_advsafe(stats).startswith("KILL")
