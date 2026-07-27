"""Contract: Wave AN4 H-FASTEDGE — generative wall_ms>0 vs AM FASTNEXT."""

from __future__ import annotations

from fastedge_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTEDGE_ID,
    FASTEDGE_N,
    FASTNEXT_HOT_WALL_MS,
    MIN_GEN_MEAN,
    WALL_DROP_MIN,
    decide_fastedge,
    fastedge_generate,
    fastedge_stats,
    mean_ms,
    score_fastedge_gen,
    score_fastedge_lookup,
    ttft_of,
)
from fastpeak_ops import AF_RAW_OPEN_WALL_MS as FP_AF


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AN4 H-FASTEDGE
    assert FASTEDGE_ID == "H-FASTEDGE"
    assert FASTEDGE_N == 10
    assert AF_RAW_OPEN_WALL_MS == FP_AF
    assert FASTNEXT_HOT_WALL_MS == 0.17
    assert MIN_GEN_MEAN == 5.0
    assert WALL_DROP_MIN == 0.20


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0
    assert mean_ms([10.0, 20.0]) == 15.0


def test_given_lookup_true_hit_when_score_then_not_speed_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_fastedge_lookup(
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
    _score, err, notes = score_fastedge_gen(
        completion="anything",
        expected_gold="gold",
        payload=payload,
    )
    assert err is True
    assert any("wall_ms" in n for n in notes)


def test_given_gen_periods_when_score_then_low_but_telemetry_ok() -> None:
    payload = {"mode": "PEAK_FAST+GENEDGE", "wall_ms": 0.12, "n_new": 16}
    score, err, notes = score_fastedge_gen(
        completion="........",
        expected_gold="mnemonic",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert any("FASTNEXT" in n for n in notes)


def test_given_chunks_when_fastedge_generate_then_wall_and_peak() -> None:
    # GIVEN curated-like chunks WHEN GENEDGE peak-fast THEN wall>0 ∧ n_new>0
    chunks = [
        "| ENT | CS | ENT+CS | MS |\n| 192 | 6 | 198 | 18 |",
        "BIP-39 mnemonic: 192-bit ENT yields 18 words.",
    ]
    payload = fastedge_generate(
        question="BIP-39: for 192-bit ENT, how many mnemonic words?",
        chunks=chunks,
    )
    assert payload["wall_ms"] > 0.0
    assert int(payload["n_new"]) > 0
    assert payload["mode"] == "PEAK_FAST+GENEDGE"
    assert "18" in str(payload["completion"])


def test_given_beats_fastnext_when_decide_then_promote() -> None:
    stats = fastedge_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=0.28,
        warm_wall_ms=0.14,
        hot_wall_ms=0.12,
        cold_ttft_ms=0.28,
        warm_ttft_ms=0.14,
        hot_ttft_ms=0.12,
        cold_e2e_ms=2.8,
        warm_e2e_ms=1.4,
        hot_e2e_ms=1.1,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_gen_telemetry"] is True
    assert stats["pass_vs_fastnext"] is True
    assert stats["pass_quality_floor"] is True
    assert decide_fastedge(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = fastedge_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=0.28,
        warm_wall_ms=0.14,
        hot_wall_ms=0.12,
        cold_ttft_ms=0.28,
        warm_ttft_ms=0.14,
        hot_ttft_ms=0.12,
        cold_e2e_ms=2.8,
        warm_e2e_ms=1.4,
        hot_e2e_ms=1.1,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_quality_floor"] is False
    assert decide_fastedge(stats) == "HOLD"


def test_given_no_beat_fastnext_when_decide_then_hold() -> None:
    stats = fastedge_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=0.50,
        warm_wall_ms=0.40,
        hot_wall_ms=0.35,
        cold_ttft_ms=0.50,
        warm_ttft_ms=0.40,
        hot_ttft_ms=0.35,
        cold_e2e_ms=5.0,
        warm_e2e_ms=4.0,
        hot_e2e_ms=3.5,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_vs_fastnext"] is False
    assert decide_fastedge(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastedge_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        cold_wall_ms=0.28,
        warm_wall_ms=0.14,
        hot_wall_ms=0.12,
        cold_ttft_ms=0.28,
        warm_ttft_ms=0.14,
        hot_ttft_ms=0.12,
        cold_e2e_ms=2.8,
        warm_e2e_ms=1.4,
        hot_e2e_ms=1.1,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert decide_fastedge(stats) == "KILL"
