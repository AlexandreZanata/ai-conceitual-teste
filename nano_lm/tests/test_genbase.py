"""Contract: Wave AP1 H-GENBASE — peak ablation true-gen gate (pesquisa §3)."""

from __future__ import annotations

from genbase_ops import (
    GENBASE_ID,
    GENBASE_N,
    GENBASE_PACK,
    GENPEAK_GEN_MEAN,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_genbase_peak,
    decide_genbase,
    extract_genbase_answer,
    genbase_stats,
    score_genbase_gen,
    score_genbase_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AP1 H-GENBASE
    assert GENBASE_ID == "H-GENBASE"
    assert GENBASE_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPEAK_GEN_MEAN == 9.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert len(GENBASE_PACK) == 10


def test_given_pack_when_ids_then_ap_hitl() -> None:
    for item in GENBASE_PACK:
        assert item["id"].startswith("AP-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_cs_when_extract_then_formula() -> None:
    ctx = "CS = ENT / 32\nMS = (ENT + CS) / 11"
    peak = extract_genbase_answer(
        "BIP-39: what is the formula for checksum length CS in terms "
        "of ENT? (write CS = …)",
        ctx,
    )
    assert peak == "CS = ENT / 32"


def test_given_fingerprint_when_extract_then_zero() -> None:
    ctx = "* 4 bytes: the fingerprint of the parent's key (0x00000000 if master key)"
    peak = extract_genbase_answer(
        "BIP-32 extended-key serialization: what parent fingerprint "
        "value is used for a master key (hex)?",
        ctx,
    )
    assert peak == "0x00000000"


def test_given_p2wpkh_when_extract_then_acronym() -> None:
    ctx = (
        "witness program is 20 bytes (''L = 20''):\n"
        "* It is interpreted as a pay-to-witness-public-key-hash (P2WPKH) program."
    )
    peak = extract_genbase_answer(
        "BIP-141: a version-0 witness program of length L=20 is "
        "interpreted as which program type (acronym)?",
        ctx,
    )
    assert peak == "P2WPKH"


def test_given_tx_when_extract_then_path() -> None:
    ctx = "#### Transactions\n`GET /rest/tx/<TX-HASH>.<bin|hex|json>`"
    peak = extract_genbase_answer(
        "Bitcoin Core REST: which GET path pattern returns a "
        "transaction by hash (include encoding suffixes)?",
        ctx,
    )
    assert peak == "GET /rest/tx/<TX-HASH>.<bin|hex|json>"


def test_given_protocol_when_extract_then_8() -> None:
    ctx = "Protocol:  8 bits\nThis field indicates the next level protocol"
    peak = extract_genbase_answer(
        "RFC 791: how many bits is the Protocol field of the "
        "Internet header?",
        ctx,
    )
    assert peak == "8"


def test_given_isize_when_extract_then_pair() -> None:
    ctx = (
        "The primary situation in which you'd use `isize` or `usize` "
        "is when indexing some sort of collection."
    )
    peak = extract_genbase_answer(
        "From Rust's data-types chapter: which integer type pair is "
        "used primarily when indexing a collection? (write both names)",
        ctx,
    )
    assert peak == "isize or usize"


def test_given_append_when_extract_then_method() -> None:
    ctx = "a.append(x) is equivalent to list.append"
    peak = extract_genbase_answer(
        "Add item `x` to the end of list `a` — one method call.",
        ctx,
    )
    assert peak == "a.append(x)"


def test_given_struct_dots_when_peak_then_used() -> None:
    text, used, span = apply_genbase_peak(
        decode_text="Once upon a time.",
        question=(
            "Rust structs chapter: which two-character token starts the "
            "trailing field-copy from another instance (e.g. `..user1`)?"
        ),
        context="### Creating Instances with Struct Update Syntax\nThe `..user1`",
    )
    assert used is True
    assert text == ".."
    assert span == ".."

    text, used, span = apply_genbase_peak(
        decode_text="Once upon a time.",
        question=(
            "BIP-39: what is the formula for checksum length CS in terms "
            "of ENT? (write CS = …)"
        ),
        context="CS = ENT / 32\nMS = (ENT + CS) / 11",
    )
    assert used is True
    assert text == "CS = ENT / 32"
    assert span == "CS = ENT / 32"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_genbase_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("GENBASE LOOKUP" in n or "not" in n.lower() for n in notes)


def test_given_ablated_drift_when_score_then_soft() -> None:
    payload = {
        "mode": "QPFB2",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
    }
    score, err, _notes = score_genbase_gen(
        completion="Once upon a time there was a little",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score <= 4.0
    assert err is True


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = genbase_stats(
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
    assert decide_genbase(stats) == "PROMOTE"


def test_given_ablated_low_when_decide_then_hold() -> None:
    stats = genbase_stats(
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
    assert decide_genbase(stats) == "HOLD"
