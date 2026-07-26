"""Contract: Wave AK4 H-FASTMORE — generative wall_ms>0 vs AJ FASTPEAK."""

from __future__ import annotations

from fastmore_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTMORE_ID,
    FASTMORE_N,
    FASTPEAK_HOT_WALL_MS,
    MIN_GEN_MEAN,
    WALL_DROP_MIN,
    decide_fastmore,
    fastmore_generate,
    fastmore_stats,
    mean_ms,
    score_fastmore_gen,
    score_fastmore_lookup,
    ttft_of,
)
from fastpeak_ops import AF_RAW_OPEN_WALL_MS as FP_AF


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AK4 H-FASTMORE
    assert FASTMORE_ID == "H-FASTMORE"
    assert FASTMORE_N == 10
    assert AF_RAW_OPEN_WALL_MS == FP_AF
    assert FASTPEAK_HOT_WALL_MS == 5.0
    assert MIN_GEN_MEAN == 5.0
    assert WALL_DROP_MIN == 0.20


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0
    assert mean_ms([10.0, 20.0]) == 15.0


def test_given_lookup_true_hit_when_score_then_not_speed_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_fastmore_lookup(
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
    _score, err, notes = score_fastmore_gen(
        completion="anything",
        expected_gold="gold",
        payload=payload,
    )
    assert err is True
    assert any("wall_ms" in n for n in notes)


def test_given_gen_periods_when_score_then_low_but_telemetry_ok() -> None:
    payload = {"mode": "PEAK_FAST+GENTRUE", "wall_ms": 4.0, "n_new": 16}
    score, err, notes = score_fastmore_gen(
        completion="........",
        expected_gold="mnemonic",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert any("FASTPEAK" in n for n in notes)


def test_given_chunks_when_fastmore_generate_then_wall_and_peak() -> None:
    # GIVEN curated-like chunks WHEN GENTRUE peak-fast THEN wall>0 ∧ n_new>0
    chunks = [
        "BIP-39 allowed ENT size range is 128-256 bits for mnemonics.",
        "Unrelated filler about wallets and seeds.",
    ]
    payload = fastmore_generate(
        question=(
            "BIP-39: what is the allowed ENT size range in bits "
            "(write low-high)?"
        ),
        chunks=chunks,
    )
    assert payload["wall_ms"] > 0.0
    assert int(payload["n_new"]) > 0
    assert payload["mode"] == "PEAK_FAST+GENTRUE"
    assert "128-256" in str(payload["completion"])


def test_given_beats_fastpeak_when_decide_then_promote() -> None:
    stats = fastmore_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=5.5,
        warm_wall_ms=4.0,
        hot_wall_ms=3.8,
        cold_ttft_ms=5.5,
        warm_ttft_ms=4.0,
        hot_ttft_ms=3.8,
        cold_e2e_ms=60.0,
        warm_e2e_ms=40.0,
        hot_e2e_ms=38.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_gen_telemetry"] is True
    assert stats["pass_vs_fastpeak"] is True
    assert stats["pass_quality_floor"] is True
    assert decide_fastmore(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = fastmore_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=5.5,
        warm_wall_ms=4.0,
        hot_wall_ms=3.8,
        cold_ttft_ms=5.5,
        warm_ttft_ms=4.0,
        hot_ttft_ms=3.8,
        cold_e2e_ms=60.0,
        warm_e2e_ms=40.0,
        hot_e2e_ms=38.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_quality_floor"] is False
    assert decide_fastmore(stats) == "HOLD"


def test_given_no_beat_fastpeak_when_decide_then_hold() -> None:
    stats = fastmore_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=8.0,
        warm_wall_ms=7.5,
        hot_wall_ms=7.0,
        cold_ttft_ms=8.0,
        warm_ttft_ms=7.5,
        hot_ttft_ms=7.0,
        cold_e2e_ms=80.0,
        warm_e2e_ms=75.0,
        hot_e2e_ms=70.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_vs_fastpeak"] is False
    assert decide_fastmore(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastmore_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        cold_wall_ms=5.5,
        warm_wall_ms=4.0,
        hot_wall_ms=3.8,
        cold_ttft_ms=5.5,
        warm_ttft_ms=4.0,
        hot_ttft_ms=3.8,
        cold_e2e_ms=60.0,
        warm_e2e_ms=40.0,
        hot_e2e_ms=38.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert decide_fastmore(stats) == "KILL"
