"""Contract: Wave AI1 H-GENPLUS — dual-arm gen push (pesquisa §5)."""

from __future__ import annotations

from genplus_ops import (
    GENLIFT_GEN_MEAN,
    GENPLUS_ID,
    GENPLUS_N,
    GENPLUS_PACK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    chunk_doc,
    decide_genplus,
    genplus_stats,
    ground_prompt,
    normalize_gen_answer,
    prefer_context_beam,
    score_genplus_gen,
    score_genplus_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AI1 H-GENPLUS
    assert GENPLUS_ID == "H-GENPLUS"
    assert GENPLUS_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert GENLIFT_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(GENPLUS_PACK) == 10


def test_given_pack_when_ids_then_ai_hitl() -> None:
    for item in GENPLUS_PACK:
        assert item["id"].startswith("AI-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_doc_when_chunk_then_windows() -> None:
    chunks = chunk_doc("word " * 200, win=80, stride=40)
    assert len(chunks) >= 2
    assert all(len(c) >= 40 for c in chunks)


def test_given_chunks_when_ground_then_context_frame() -> None:
    prompt = ground_prompt(
        "What is f64?",
        chunks=["Rust default float is f64 in examples."],
        k=1,
    )
    assert "Context:" in prompt
    assert "Short factual answer" in prompt
    assert "What is f64?" in prompt


def test_given_long_prompt_when_fit_then_tail_kept() -> None:
    from genplus_ops import fit_prompt_tokens

    long = "x" * 2000 + "\nQuestion: q?\nShort factual answer:"
    out = fit_prompt_tokens(long, max_chars=400)
    assert len(out) <= 400
    assert out.endswith("Short factual answer:")


def test_given_beams_when_prefer_context_then_non_period() -> None:
    text, idx, used = prefer_context_beam(
        ["........", "f64 is the default float type"],
        context="Rust floating-point default is f64",
    )
    assert used is True
    assert idx == 1
    assert "f64" in text


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_genplus_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD",
        "wall_ms": 40.0,
        "n_new": 16,
    }
    score, err, notes = score_genplus_gen(
        completion="........",
        expected_gold="anything",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert notes


def test_given_gen_contains_gold_when_score_then_seven() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD",
        "wall_ms": 50.0,
        "n_new": 32,
    }
    score, err, notes = score_genplus_gen(
        completion="The serialization length is 78 bytes before Base58.",
        expected_gold="78",
        payload=payload,
    )
    assert score == 7.0 and err is False
    assert any("contained" in n for n in notes)


def test_given_gen_exact_when_score_then_nine() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD",
        "wall_ms": 50.0,
        "n_new": 8,
    }
    score, err, _notes = score_genplus_gen(
        completion="f64",
        expected_gold="f64",
        payload=payload,
    )
    assert score == 9.0 and err is False


def test_given_normalize_when_multiline_then_first_line() -> None:
    assert normalize_gen_answer("f64\nmore junk here") == "f64"


def test_given_ready_gen_when_decide_then_promote() -> None:
    stats = genplus_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
    )
    assert stats["pass_gen"] is True
    assert stats["beats_genlift_gen"] is True
    assert decide_genplus(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = genplus_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
    )
    assert stats["pass_gen"] is False
    assert decide_genplus(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = genplus_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
    )
    assert decide_genplus(stats) == "KILL"
