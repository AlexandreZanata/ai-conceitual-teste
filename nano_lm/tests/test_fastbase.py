"""Contract: Wave AP4 H-FASTBASE — generative wall_ms>0 vs AO FASTCORE."""

from __future__ import annotations

from fastbase_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTBASE_ID,
    FASTBASE_N,
    FASTCORE_HOT_WALL_MS,
    FASTCORE_WARM_WALL_MS,
    MIN_GEN_MEAN,
    WALL_DROP_MIN,
    decide_fastbase,
    fastbase_generate,
    fastbase_stats,
    mean_ms,
    score_fastbase_gen,
    score_fastbase_lookup,
    ttft_of,
)
from fastpeak_ops import AF_RAW_OPEN_WALL_MS as FP_AF


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AP4 H-FASTBASE
    assert FASTBASE_ID == "H-FASTBASE"
    assert FASTBASE_N == 10
    assert AF_RAW_OPEN_WALL_MS == FP_AF
    assert FASTCORE_HOT_WALL_MS == 0.05
    assert FASTCORE_WARM_WALL_MS == 0.06
    assert MIN_GEN_MEAN == 5.0
    assert WALL_DROP_MIN == 0.20


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0
    assert mean_ms([10.0, 20.0]) == 15.0


def test_given_lookup_true_hit_when_score_then_not_speed_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_fastbase_lookup(
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
    _score, err, notes = score_fastbase_gen(
        completion="anything",
        expected_gold="gold",
        payload=payload,
    )
    assert err is True
    assert any("wall_ms" in n for n in notes)


def test_given_gen_periods_when_score_then_low_but_telemetry_ok() -> None:
    payload = {"mode": "PEAK_FAST+GENBASE", "wall_ms": 0.12, "n_new": 16}
    score, err, notes = score_fastbase_gen(
        completion="........",
        expected_gold="mnemonic",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert any("FASTCORE" in n for n in notes)


def test_given_struct_update_dots_when_score_then_floor() -> None:
    payload = {"mode": "PEAK_FAST+GENBASE", "wall_ms": 0.04, "n_new": 1}
    score, err, notes = score_fastbase_gen(
        completion="..",
        expected_gold="..",
        payload=payload,
    )
    assert score >= 5.0 and err is False
    assert any("struct-update" in n for n in notes)


def test_given_chunks_when_fastbase_generate_then_wall_and_peak() -> None:
    # GIVEN curated-like chunks WHEN GENBASE peak-fast THEN wall>0 ∧ n_new>0
    chunks = [
        "The checksum length is CS = ENT / 32.",
        "BIP-39: checksum length CS formula uses ENT.",
    ]
    payload = fastbase_generate(
        question=(
            "BIP-39: what is the formula for checksum length CS "
            "in terms of ENT? (write CS = …)"
        ),
        chunks=chunks,
    )
    assert payload["wall_ms"] > 0.0
    assert int(payload["n_new"]) > 0
    assert payload["mode"] == "PEAK_FAST+GENBASE"
    assert "ENT" in str(payload["completion"]) or "32" in str(
        payload["completion"]
    )


def test_given_beats_fastcore_when_decide_then_promote() -> None:
    stats = fastbase_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=0.12,
        warm_wall_ms=0.05,
        hot_wall_ms=0.04,
        cold_ttft_ms=0.12,
        warm_ttft_ms=0.05,
        hot_ttft_ms=0.04,
        cold_e2e_ms=1.2,
        warm_e2e_ms=0.5,
        hot_e2e_ms=0.4,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_gen_telemetry"] is True
    assert stats["pass_vs_fastcore"] is True
    assert stats["pass_quality_floor"] is True
    assert decide_fastbase(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = fastbase_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=0.12,
        warm_wall_ms=0.05,
        hot_wall_ms=0.04,
        cold_ttft_ms=0.12,
        warm_ttft_ms=0.05,
        hot_ttft_ms=0.04,
        cold_e2e_ms=1.2,
        warm_e2e_ms=0.5,
        hot_e2e_ms=0.4,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_quality_floor"] is False
    assert decide_fastbase(stats) == "HOLD"


def test_given_no_beat_fastcore_when_decide_then_hold() -> None:
    stats = fastbase_stats(
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
    assert stats["pass_vs_fastcore"] is False
    assert decide_fastbase(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastbase_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[7.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        cold_wall_ms=0.12,
        warm_wall_ms=0.05,
        hot_wall_ms=0.04,
        cold_ttft_ms=0.12,
        warm_ttft_ms=0.05,
        hot_ttft_ms=0.04,
        cold_e2e_ms=1.2,
        warm_e2e_ms=0.5,
        hot_e2e_ms=0.4,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert decide_fastbase(stats) == "KILL"
