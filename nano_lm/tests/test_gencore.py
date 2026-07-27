"""Contract: Wave AO1 H-GENCORE — peak ablation true-gen gate (pesquisa §3)."""

from __future__ import annotations

from gencore_ops import (
    GENCORE_ID,
    GENCORE_N,
    GENCORE_PACK,
    GENPEAK_GEN_MEAN,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_gencore_peak,
    decide_gencore,
    extract_gencore_answer,
    gencore_stats,
    score_gencore_gen,
    score_gencore_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AO1 H-GENCORE
    assert GENCORE_ID == "H-GENCORE"
    assert GENCORE_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPEAK_GEN_MEAN == 9.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(GENCORE_PACK) == 10


def test_given_pack_when_ids_then_ao_hitl() -> None:
    for item in GENCORE_PACK:
        assert item["id"].startswith("AO-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_ent224_when_extract_then_21() -> None:
    ctx = "|  224  |  7 |   231  |  21  |"
    peak = extract_gencore_answer(
        "BIP-39: for 224-bit ENT, how many mnemonic words?",
        ctx,
    )
    assert peak == "21"


def test_given_version_when_extract_then_4() -> None:
    ctx = (
        "* 4 bytes: version bytes (mainnet: 0x0488B21E public, "
        "0x0488ADE4 private)"
    )
    peak = extract_gencore_answer(
        "BIP-32 extended-key serialization: how many bytes is the "
        "version field?",
        ctx,
    )
    assert peak == "4"


def test_given_witness_program_when_extract_then_40() -> None:
    ctx = (
        "Then, a byte L between 0x02 (push of 2 bytes) and 0x28 "
        "(push of 40 bytes) inclusive."
    )
    peak = extract_gencore_answer(
        "BIP-141: what is the maximum witness program length L "
        "in bytes (≤ N)?",
        ctx,
    )
    assert peak == "40"


def test_given_block_when_extract_then_path() -> None:
    ctx = (
        "#### Blocks "
        "`GET /rest/block/<BLOCK-HASH>.<bin|hex|json>`"
    )
    peak = extract_gencore_answer(
        "Bitcoin Core REST: which GET path pattern returns a full "
        "block by hash (include encoding suffixes)?",
        ctx,
    )
    assert peak == "GET /rest/block/<BLOCK-HASH>.<bin|hex|json>"


def test_given_ttl_when_extract_then_8() -> None:
    ctx = (
        "Time to Live, Options, and Header Checksum.\n"
        "Time to Live:  8 bits\n"
        "This field indicates the maximum time"
    )
    peak = extract_gencore_answer(
        "RFC 791: how many bits is the Time to Live (TTL) field of "
        "the Internet header?",
        ctx,
    )
    assert peak == "8"


def test_given_count_when_extract_then_method() -> None:
    ctx = "list.count(x) — Return the number of times value appears"
    peak = extract_gencore_answer(
        "Return how many times value `x` appears in list `a` — "
        "one method call.",
        ctx,
    )
    assert peak == "a.count(x)"


def test_given_peak_apply_when_span_then_used() -> None:
    text, used, span = apply_gencore_peak(
        decode_text="Once upon a time.",
        question="BIP-39: for 224-bit ENT, how many mnemonic words?",
        context="|  224  |  7 |   231  |  21  |",
    )
    assert used is True
    assert text == "21"
    assert span == "21"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_gencore_lookup(
        mode="WRAP_LOOKUP",
        completion="21",
        expected_gold="21",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("GENCORE LOOKUP" in n or "not" in n.lower() for n in notes)


def test_given_ablated_drift_when_score_then_soft() -> None:
    payload = {
        "mode": "QPFB2",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
    }
    score, err, _notes = score_gencore_gen(
        completion="Once upon a time there was a little",
        expected_gold="21",
        payload=payload,
        peak_ablated=True,
    )
    assert score <= 4.0
    assert err is True


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = gencore_stats(
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
    assert decide_gencore(stats) == "PROMOTE"


def test_given_ablated_low_when_decide_then_hold() -> None:
    stats = gencore_stats(
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
    assert decide_gencore(stats) == "HOLD"
