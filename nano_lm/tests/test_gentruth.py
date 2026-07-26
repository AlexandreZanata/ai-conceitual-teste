"""Contract: Wave AM1 H-GENTRUTH — peak ablation true-gen gate (pesquisa §3)."""

from __future__ import annotations

from gentruth_ops import (
    GENPEAK_GEN_MEAN,
    GENPLUS_GEN_MEAN,
    GENTRUTH_ID,
    GENTRUTH_N,
    GENTRUTH_PACK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_gentruth_peak,
    decide_gentruth,
    extract_gentruth_answer,
    gentruth_stats,
    score_gentruth_gen,
    score_gentruth_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AM1 H-GENTRUTH
    assert GENTRUTH_ID == "H-GENTRUTH"
    assert GENTRUTH_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPEAK_GEN_MEAN == 9.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(GENTRUTH_PACK) == 10


def test_given_pack_when_ids_then_am_hitl() -> None:
    for item in GENTRUTH_PACK:
        assert item["id"].startswith("AM-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_ent160_when_extract_then_15() -> None:
    ctx = "|  160  |  5 |   165  |  15  |"
    peak = extract_gentruth_answer(
        "BIP-39: for 160-bit ENT, how many mnemonic words?",
        ctx,
    )
    assert peak == "15"


def test_given_key_data_when_extract_then_33() -> None:
    ctx = (
        "33 bytes: the public key or private key data "
        "(ser_P(K) for public keys, 0x00 || ser_256(k) for private keys)"
    )
    peak = extract_gentruth_answer(
        "BIP-32 extended-key serialization: how many bytes is the "
        "key data field (public or private)?",
        ctx,
    )
    assert peak == "33"


def test_given_p2wpkh_when_extract_then_2() -> None:
    ctx = (
        "It is interpreted as a pay-to-witness-public-key-hash (P2WPKH) "
        "program. The witness must consist of exactly 2 items "
        "(≤ 520 bytes each)."
    )
    peak = extract_gentruth_answer(
        "BIP-141: how many witness stack items MUST a version-0 "
        "P2WPKH input provide?",
        ctx,
    )
    assert peak == "2"


def test_given_mempool_contents_when_extract_then_path() -> None:
    ctx = "`GET /rest/mempool/contents.json` returns mempool contents."
    peak = extract_gentruth_answer(
        "Bitcoin Core REST: which GET path returns mempool contents "
        "as JSON?",
        ctx,
    )
    assert peak == "GET /rest/mempool/contents.json"


def test_given_ihl_when_extract_then_4() -> None:
    ctx = "IHL:  4 bits"
    peak = extract_gentruth_answer(
        "RFC 791: how many bits is the IHL field of the Internet header?",
        ctx,
    )
    assert peak == "4"


def test_given_char_bytes_when_extract_then_4_not_unicode_range() -> None:
    ctx = (
        "Rust's `char` type is 4 bytes in size and represents a Unicode "
        "scalar value ... Unicode scalar values range from `U+0000` to "
        "`U+D7FF` and `U+E000` to `U+10FFFF` inclusive."
    )
    peak = extract_gentruth_answer(
        "From Rust's data-types chapter: how many bytes is a `char` value?",
        ctx,
    )
    assert peak == "4"


def test_given_decode_when_apply_peak_then_prefer_span() -> None:
    text, used, peak = apply_gentruth_peak(
        decode_text="Once upon a time........",
        question=(
            "Name the built-in that sets a named attribute on an "
            "object (listed with getattr/delattr)."
        ),
        context="getattr(), setattr() and delattr(), as well as when referencing",
    )
    assert used is True
    assert peak == "setattr"
    assert text == "setattr"


def test_given_lookup_true_when_score_then_high() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_gentruth_lookup(
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
    score, err, notes = score_gentruth_gen(
        completion="15",
        expected_gold="15",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 9.0 and err is False
    assert any("true gen" in n for n in notes)


def test_given_peak_only_lift_when_decide_then_hold() -> None:
    stats = gentruth_stats(
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
    assert decide_gentruth(stats) == "HOLD"


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = gentruth_stats(
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
    assert decide_gentruth(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = gentruth_stats(
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
    assert decide_gentruth(stats) == "KILL"
