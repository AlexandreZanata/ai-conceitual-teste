"""Contract: Wave AN1 H-GENEDGE — peak ablation true-gen gate (pesquisa §3)."""

from __future__ import annotations

from genedge_ops import (
    GENEDGE_ID,
    GENEDGE_N,
    GENEDGE_PACK,
    GENPEAK_GEN_MEAN,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_genedge_peak,
    decide_genedge,
    extract_genedge_answer,
    genedge_stats,
    score_genedge_gen,
    score_genedge_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AN1 H-GENEDGE
    assert GENEDGE_ID == "H-GENEDGE"
    assert GENEDGE_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPEAK_GEN_MEAN == 9.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(GENEDGE_PACK) == 10


def test_given_pack_when_ids_then_an_hitl() -> None:
    for item in GENEDGE_PACK:
        assert item["id"].startswith("AN-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_ent192_when_extract_then_18() -> None:
    ctx = "|  192  |  6 |   198  |  18  |"
    peak = extract_genedge_answer(
        "BIP-39: for 192-bit ENT, how many mnemonic words?",
        ctx,
    )
    assert peak == "18"


def test_given_child_number_when_extract_then_4() -> None:
    ctx = "* 4 bytes: child number. This is ser_32(i) for i in xi"
    peak = extract_genedge_answer(
        "BIP-32 extended-key serialization: how many bytes is the "
        "child number field?",
        ctx,
    )
    assert peak == "4"


def test_given_witnessscript_when_extract_then_10000() -> None:
    ctx = (
        "The witnessScript (≤ 10,000 bytes) is popped off the "
        "initial witness stack."
    )
    peak = extract_genedge_answer(
        "BIP-141 P2WSH: what is the maximum witnessScript size "
        "in bytes (≤ N)?",
        ctx,
    )
    assert peak == "10000"


def test_given_headers_when_extract_then_path() -> None:
    ctx = (
        "#### Blockheaders "
        "`GET /rest/headers/<BLOCK-HASH>.<bin|hex|json>?count=<COUNT=5>`"
    )
    peak = extract_genedge_answer(
        "Bitcoin Core REST: which GET path pattern returns "
        "blockheaders (include encoding suffixes)?",
        ctx,
    )
    assert peak == "GET /rest/headers/<BLOCK-HASH>.<bin|hex|json>"


def test_given_total_length_when_extract_then_16() -> None:
    ctx = "Total Length:  16 bits"
    peak = extract_genedge_answer(
        "RFC 791: how many bits is the Total Length field of the "
        "Internet header?",
        ctx,
    )
    assert peak == "16"


def test_given_tuple_structs_when_extract_then_label() -> None:
    ctx = (
        "structs that look similar to tuples, called _tuple structs_. "
        "Tuple structs have the added meaning"
    )
    peak = extract_genedge_answer(
        "Rust structs chapter: what name is given to structs that "
        "look like tuples but carry a type name?",
        ctx,
    )
    assert peak == "tuple structs"


def test_given_decode_when_apply_peak_then_prefer_span() -> None:
    text, used, peak = apply_genedge_peak(
        decode_text="Once upon a time........",
        question=(
            "Name the instance attribute that stores writable "
            "attributes as a dictionary."
        ),
        context="as well as when referencing __dict__ directly.",
    )
    assert used is True
    assert peak == "__dict__"
    assert text == "__dict__"


def test_given_lookup_true_when_score_then_high() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_genedge_lookup(
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
    score, err, notes = score_genedge_gen(
        completion="18",
        expected_gold="18",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 9.0 and err is False
    assert any("true gen" in n for n in notes)


def test_given_peak_only_lift_when_decide_then_hold() -> None:
    stats = genedge_stats(
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
    assert decide_genedge(stats) == "HOLD"


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = genedge_stats(
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
    assert decide_genedge(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = genedge_stats(
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
    assert decide_genedge(stats) == "KILL"
