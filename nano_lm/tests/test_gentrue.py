"""Contract: Wave AK1 H-GENTRUE — peak ablation true-gen gate (pesquisa §3)."""

from __future__ import annotations

from gentrue_ops import (
    GENPEAK_GEN_MEAN,
    GENTRUE_ID,
    GENTRUE_N,
    GENTRUE_PACK,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_gentrue_peak,
    decide_gentrue,
    extract_gentrue_answer,
    gentrue_stats,
    score_gentrue_gen,
    score_gentrue_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AK1 H-GENTRUE
    assert GENTRUE_ID == "H-GENTRUE"
    assert GENTRUE_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPEAK_GEN_MEAN == 9.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(GENTRUE_PACK) == 10


def test_given_pack_when_ids_then_ak_hitl() -> None:
    for item in GENTRUE_PACK:
        assert item["id"].startswith("AK-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_ent_range_when_extract_then_128_256() -> None:
    ctx = "The allowed size of ENT is 128-256 bits."
    peak = extract_gentrue_answer(
        "BIP-39: what is the allowed ENT size range in bits (write low-high)?",
        ctx,
    )
    assert peak == "128-256"


def test_given_marker_when_extract_then_0x00() -> None:
    ctx = "The marker MUST be a 1-byte zero value: 0x00."
    peak = extract_gentrue_answer(
        "BIP-141: what hex value MUST the 1-byte witness serialization marker be?",
        ctx,
    )
    assert peak == "0x00"


def test_given_mempool_when_extract_then_path() -> None:
    ctx = "`GET /rest/mempool/info.json` returns mempool info."
    peak = extract_gentrue_answer(
        "Bitcoin Core REST: which GET path returns mempool info as JSON?",
        ctx,
    )
    assert peak == "GET /rest/mempool/info.json"


def test_given_decode_when_apply_peak_then_prefer_span() -> None:
    text, used, peak = apply_gentrue_peak(
        decode_text="Once upon a time........",
        question="Which statement breaks out of the innermost enclosing loop?",
        context="The break statement breaks out of the innermost enclosing loop.",
    )
    assert used is True
    assert peak == "break"
    assert text == "break"


def test_given_lookup_true_when_score_then_high() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_gentrue_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_ablated_exact_when_score_then_nine() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 50.0,
        "n_new": 32,
        "peak_used": False,
    }
    score, err, notes = score_gentrue_gen(
        completion="128-256",
        expected_gold="128-256",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 9.0 and err is False
    assert any("true gen" in n for n in notes)


def test_given_peak_on_when_score_then_labeled_extractive() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 50.0,
        "n_new": 32,
        "peak_used": True,
    }
    score, err, notes = score_gentrue_gen(
        completion="128-256",
        expected_gold="128-256",
        payload=payload,
        peak_ablated=False,
    )
    assert score == 9.0 and err is False
    assert any("NOT open-chat IQ" in n for n in notes)


def test_given_ablated_with_peak_flag_when_score_then_error() -> None:
    payload = {
        "mode": "bad",
        "wall_ms": 50.0,
        "n_new": 8,
        "peak_used": True,
    }
    score, err, notes = score_gentrue_gen(
        completion="x",
        expected_gold="x",
        payload=payload,
        peak_ablated=True,
    )
    assert err is True
    assert score == 4.0
    assert any("must not use peak" in n for n in notes)


def test_given_peak_only_lift_when_decide_then_hold() -> None:
    stats = gentrue_stats(
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
    assert stats["peak_only_lift"] is True
    assert stats["pass_gen"] is False
    assert decide_gentrue(stats) == "HOLD"


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = gentrue_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        gen_peak_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert decide_gentrue(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = gentrue_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        gen_peak_scores=[9.0] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert decide_gentrue(stats) == "KILL"
