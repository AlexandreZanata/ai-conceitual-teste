"""Contract: Wave AQ6 H-NANOGEN — ablated gen gate (pesquisa §5)."""

from __future__ import annotations

from nanogen_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    NANOGEN_ID,
    NANOGEN_N,
    NANOGEN_PACK,
    NANOGEN_THESIS,
    decide_nanogen,
    nanogen_stats,
    score_nanogen_gen,
    score_nanogen_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ6 — ablated mean ≥5 PROMOTE else HOLD
    assert NANOGEN_ID == "H-NANOGEN"
    assert NANOGEN_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert len(NANOGEN_PACK) == 10
    assert "ablated" in NANOGEN_THESIS.lower() or "5.0" in NANOGEN_THESIS


def test_given_pack_when_kinds_then_held_and_para() -> None:
    kinds = [p["kind"] for p in NANOGEN_PACK]
    assert kinds.count("held-out") == 5
    assert kinds.count("paraphrase") == 5
    for item in NANOGEN_PACK:
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_para_when_question_then_not_parent() -> None:
    for item in NANOGEN_PACK:
        if item["kind"] != "paraphrase":
            continue
        assert item["question"] != item.get("parent_question", "")


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_nanogen_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NANOGEN LOOKUP" in n or "not" in n.lower() for n in notes)


def test_given_ablated_drift_when_score_then_soft() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
    }
    score, err, _notes = score_nanogen_gen(
        completion="Once upon a time there was a little",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score <= 4.0
    assert err is True


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = nanogen_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[9.0] * 10,
        gen_errors=[False] * 10,
        gen_peak_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert stats["pass_lookup"] is True
    assert stats["pass_gen"] is True
    assert decide_nanogen(stats) == "PROMOTE"


def test_given_ablated_low_when_decide_then_hold() -> None:
    stats = nanogen_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        gen_peak_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert stats.get("peak_only_lift") is True or stats["gen_mean"] < 5.0
    assert decide_nanogen(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = nanogen_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[9.0] * 10,
        gen_errors=[False] * 10,
        gen_peak_scores=[9.0] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert decide_nanogen(stats) == "KILL"
