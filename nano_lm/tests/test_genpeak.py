"""Contract: Wave AJ1 H-GENPEAK — dual-arm gen peak (pesquisa §3)."""

from __future__ import annotations

from genpeak_ops import (
    GENPEAK_ID,
    GENPEAK_N,
    GENPEAK_PACK,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    apply_peak_completion,
    chunk_doc,
    decide_genpeak,
    extract_peak_answer,
    genpeak_stats,
    peak_top_k_chunks,
    score_genpeak_gen,
    score_genpeak_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AJ1 H-GENPEAK
    assert GENPEAK_ID == "H-GENPEAK"
    assert GENPEAK_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENPLUS_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(GENPEAK_PACK) == 10


def test_given_pack_when_ids_then_aj_hitl() -> None:
    for item in GENPEAK_PACK:
        assert item["id"].startswith("AJ-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_doc_when_peak_chunks_then_cue_boost() -> None:
    chunks = [
        "unrelated filler text about weather and cats " * 3,
        "BIP-39 mnemonic entropy ENT must be a multiple of 32 bits.",
    ]
    hits = peak_top_k_chunks(
        "BIP-39: mnemonic entropy length ENT must be a multiple of how many bits?",
        chunks,
        1,
    )
    assert hits and "32" in hits[0]


def test_given_context_when_extract_peak_then_no_gold_arg() -> None:
    ctx = (
        "If the version byte is 0, and the witness program is 32 bytes "
        "(L = 32): It is interpreted as a pay-to-witness-script-hash "
        "(P2WSH)."
    )
    peak = extract_peak_answer(
        "BIP-141: version byte 0 with a 32-byte witness program is "
        "interpreted as which program type (acronym)?",
        ctx,
    )
    assert peak == "P2WSH"


def test_given_depth_bytes_when_extract_then_one() -> None:
    ctx = (
        "* 4 bytes: version bytes\n"
        "* 1 byte: depth: 0x00 for master nodes\n"
        "* 4 bytes: the fingerprint of the parent's key\n"
    )
    peak = extract_peak_answer(
        "BIP-32 extended-key serialization: how many bytes is the depth field?",
        ctx,
    )
    assert peak == "1"


def test_given_decode_when_apply_peak_then_prefer_span() -> None:
    text, used, peak = apply_peak_completion(
        decode_text="Once upon a time a tiny story drifted........",
        question="Which statement skips the rest of the current loop iteration?",
        context="The continue statement continues with the next iteration.",
    )
    assert used is True
    assert peak == "continue"
    assert text == "continue"


def test_given_builtin_html_when_extract_then_isinstance() -> None:
    ctx = (
        'Python has two built-in functions that work with inheritance:</p>'
        '<ul class="simple"><li><p>Use '
        '<a href="../library/functions.html#isinstance" '
        'title="isinstance"><code class="xref"><span class="pre">'
        "BaseClassName</span></code></a>"
    )
    peak = extract_peak_answer(
        "Name the built-in that checks an instance's type "
        "(tutorial inheritance tip).",
        ctx,
    )
    assert peak == "isinstance"


    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_genpeak_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_peak_exact_when_score_then_nine() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 50.0,
        "n_new": 32,
        "peak_used": True,
    }
    score, err, notes = score_genpeak_gen(
        completion="32",
        expected_gold="32",
        payload=payload,
    )
    assert score == 9.0 and err is False
    assert any("exact" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 40.0,
        "n_new": 16,
        "peak_used": False,
    }
    score, err, _notes = score_genpeak_gen(
        completion="........",
        expected_gold="anything",
        payload=payload,
    )
    assert score == 1.0 and err is True


def test_given_ready_gen_when_decide_then_promote() -> None:
    stats = genpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert stats["pass_gen"] is True
    assert stats["beats_genplus_gen"] is True
    assert decide_genpeak(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = genpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=0,
    )
    assert stats["pass_gen"] is False
    assert decide_genpeak(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = genpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
        n_peak=10,
    )
    assert decide_genpeak(stats) == "KILL"


def test_given_chunk_doc_when_windows_then_ok() -> None:
    chunks = chunk_doc("word " * 200, win=80, stride=40)
    assert len(chunks) >= 2
