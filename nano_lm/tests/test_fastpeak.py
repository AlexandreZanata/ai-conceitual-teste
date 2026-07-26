"""Contract: Wave AJ4 H-FASTPEAK — generative wall_ms>0 vs AI FASTPUSH."""

from __future__ import annotations

from fastpeak_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTPEAK_ID,
    FASTPEAK_N,
    FASTPUSH_HOT_WALL_MS,
    WALL_DROP_MIN,
    decide_fastpeak,
    fastpeak_generate,
    fastpeak_stats,
    mean_ms,
    score_fastpeak_gen,
    score_fastpeak_lookup,
    ttft_of,
)
from fastpush_ops import AF_RAW_OPEN_WALL_MS as FP_AF


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AJ4 H-FASTPEAK
    assert FASTPEAK_ID == "H-FASTPEAK"
    assert FASTPEAK_N == 10
    assert AF_RAW_OPEN_WALL_MS == FP_AF
    assert FASTPUSH_HOT_WALL_MS == 10.7
    assert WALL_DROP_MIN == 0.20


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0
    assert mean_ms([10.0, 20.0]) == 15.0


def test_given_lookup_true_hit_when_score_then_not_speed_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_fastpeak_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NOT speed IQ" in n for n in notes)


def test_given_gen_zero_wall_when_score_then_error() -> None:
    payload = {"mode": "ASKFAST_CACHE", "wall_ms": 0.0, "n_new": 0}
    _score, err, notes = score_fastpeak_gen(
        completion="anything",
        expected_gold="gold",
        payload=payload,
    )
    assert err is True
    assert any("wall_ms" in n for n in notes)


def test_given_gen_periods_when_score_then_low_but_telemetry_ok() -> None:
    payload = {"mode": "QT+EARLY n=1", "wall_ms": 10.0, "n_new": 16}
    score, err, notes = score_fastpeak_gen(
        completion="........",
        expected_gold="mnemonic",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert any("FASTPUSH" in n for n in notes)


def test_given_chunks_when_fastpeak_generate_then_wall_and_peak() -> None:
    # GIVEN curated-like chunks WHEN peak-fast gen THEN wall_ms>0 ∧ n_new>0
    chunks = [
        "Entropy must be a multiple of 32 bits for BIP-0039 mnemonics.",
        "Unrelated filler about wallets and seeds.",
    ]
    payload = fastpeak_generate(
        question="BIP-0039 entropy multiple of how many bits?",
        chunks=chunks,
    )
    assert payload["wall_ms"] > 0.0
    assert int(payload["n_new"]) > 0
    assert payload["mode"] == "PEAK_FAST+EXTRACTIVE"
    assert "32" in str(payload["completion"])


def test_given_beats_fastpush_when_decide_then_promote() -> None:
    stats = fastpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=25.0,
        warm_wall_ms=10.0,
        hot_wall_ms=9.5,
        cold_ttft_ms=25.0,
        warm_ttft_ms=10.0,
        hot_ttft_ms=9.5,
        cold_e2e_ms=3000.0,
        warm_e2e_ms=1100.0,
        hot_e2e_ms=1000.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_gen_telemetry"] is True
    assert stats["pass_vs_fastpush"] is True
    assert decide_fastpeak(stats) == "PROMOTE"


def test_given_no_beat_fastpush_when_decide_then_hold() -> None:
    stats = fastpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=25.0,
        warm_wall_ms=15.0,
        hot_wall_ms=14.0,
        cold_ttft_ms=25.0,
        warm_ttft_ms=15.0,
        hot_ttft_ms=14.0,
        cold_e2e_ms=3000.0,
        warm_e2e_ms=2000.0,
        hot_e2e_ms=1900.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_vs_fastpush"] is False
    assert decide_fastpeak(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        cold_wall_ms=25.0,
        warm_wall_ms=10.0,
        hot_wall_ms=9.5,
        cold_ttft_ms=25.0,
        warm_ttft_ms=10.0,
        hot_ttft_ms=9.5,
        cold_e2e_ms=3000.0,
        warm_e2e_ms=1100.0,
        hot_e2e_ms=1000.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert decide_fastpeak(stats) == "KILL"
