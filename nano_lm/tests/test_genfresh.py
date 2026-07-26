"""Contract: Wave AL1 H-GENFRESH — peak ablation true-gen gate (pesquisa §3)."""

from __future__ import annotations

from genfresh_ops import (
    GENFRESH_ID,
    GENFRESH_N,
    GENFRESH_PACK,
    GENPEAK_GEN_MEAN,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_genfresh_peak,
    decide_genfresh,
    extract_genfresh_answer,
    genfresh_stats,
    score_genfresh_gen,
    score_genfresh_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AL1 H-GENFRESH
    assert GENFRESH_ID == "H-GENFRESH"
    assert GENFRESH_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPEAK_GEN_MEAN == 9.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(GENFRESH_PACK) == 10


def test_given_pack_when_ids_then_al_hitl() -> None:
    for item in GENFRESH_PACK:
        assert item["id"].startswith("AL-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_ent256_when_extract_then_24() -> None:
    ctx = "|  256  |  8 |   264  |  24  |"
    peak = extract_genfresh_answer(
        "BIP-39: for 256-bit ENT, how many mnemonic words?",
        ctx,
    )
    assert peak == "24"


def test_given_flag_when_extract_then_0x01() -> None:
    ctx = "The flag MUST be a 1-byte non-zero value. Currently, 0x01 MUST be used."
    peak = extract_genfresh_answer(
        "BIP-141: what hex value MUST the 1-byte witness serialization flag be?",
        ctx,
    )
    assert peak == "0x01"


def test_given_deployment_when_extract_then_path() -> None:
    ctx = "`GET /rest/deploymentinfo.json` returns deployment info."
    peak = extract_genfresh_answer(
        "Bitcoin Core REST: which GET path returns deployment info as JSON "
        "(no blockhash)?",
        ctx,
    )
    assert peak == "GET /rest/deploymentinfo.json"


def test_given_ttl_when_extract_then_8() -> None:
    ctx = "Time to Live:  8 bits"
    peak = extract_genfresh_answer(
        "RFC 791: how many bits is the Time to Live field of the Internet "
        "header?",
        ctx,
    )
    assert peak == "8"


def test_given_decode_when_apply_peak_then_prefer_span() -> None:
    text, used, peak = apply_genfresh_peak(
        decode_text="Once upon a time........",
        question="Reverse list `a` in place — one method call.",
        context="list.reverse() Reverse the elements of the list in place.",
    )
    assert used is True
    assert peak == "a.reverse()"
    assert text == "a.reverse()"


def test_given_lookup_true_when_score_then_high() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_genfresh_lookup(
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
    score, err, notes = score_genfresh_gen(
        completion="24",
        expected_gold="24",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 9.0 and err is False
    assert any("true gen" in n for n in notes)


def test_given_peak_only_lift_when_decide_then_hold() -> None:
    stats = genfresh_stats(
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
    assert decide_genfresh(stats) == "HOLD"


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = genfresh_stats(
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
    assert decide_genfresh(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = genfresh_stats(
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
    assert decide_genfresh(stats) == "KILL"
