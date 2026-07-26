"""Contract: Wave AG4 H-FASTREAL — generative wall_ms>0 vs AF raw baseline."""

from __future__ import annotations

from fastplus_ops import AB_OPEN_MEAN_WALL_MS
from fastreal_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTREAL_ID,
    FASTREAL_N,
    WALL_DROP_MIN,
    decide_fastreal,
    fastreal_stats,
    mean_ms,
    score_fastreal_gen,
    score_fastreal_lookup,
    ttft_of,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AG4 H-FASTREAL
    assert FASTREAL_ID == "H-FASTREAL"
    assert FASTREAL_N == 10
    assert AF_RAW_OPEN_WALL_MS == float(AB_OPEN_MEAN_WALL_MS)
    assert WALL_DROP_MIN == 0.20


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0
    assert mean_ms([10.0, 20.0]) == 15.0


def test_given_lookup_true_hit_when_score_then_not_speed_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_fastreal_lookup(
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
    score, err, notes = score_fastreal_gen(
        completion="anything",
        expected_gold="gold",
        payload=payload,
    )
    assert err is True
    assert any("wall_ms" in n for n in notes)
    assert score >= 0.0


def test_given_gen_periods_when_score_then_low_but_telemetry_ok() -> None:
    payload = {"mode": "QT+EARLY n=1", "wall_ms": 12.0, "n_new": 16}
    score, err, notes = score_fastreal_gen(
        completion="........",
        expected_gold="nums.extend(more)",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert any("AF raw" in n for n in notes)


def test_given_speed_and_lookup_when_decide_then_promote() -> None:
    stats = fastreal_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=20.0,
        warm_wall_ms=15.0,
        hot_wall_ms=12.0,
        cold_ttft_ms=20.0,
        warm_ttft_ms=15.0,
        hot_ttft_ms=12.0,
        cold_e2e_ms=400.0,
        warm_e2e_ms=300.0,
        hot_e2e_ms=250.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_gen_telemetry"] is True
    assert stats["pass_speed"] is True
    assert decide_fastreal(stats) == "PROMOTE"


def test_given_no_speed_when_decide_then_hold() -> None:
    # cold slower than AF raw and no warm/hot improvement
    stats = fastreal_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        cold_wall_ms=40.0,
        warm_wall_ms=40.0,
        hot_wall_ms=40.0,
        cold_ttft_ms=40.0,
        warm_ttft_ms=40.0,
        hot_ttft_ms=40.0,
        cold_e2e_ms=500.0,
        warm_e2e_ms=500.0,
        hot_e2e_ms=500.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert stats["pass_speed"] is False
    assert stats["pass_vs_af_raw"] is False
    assert decide_fastreal(stats) == "HOLD"


def test_given_false_hit_or_zero_wall_when_decide_then_kill() -> None:
    base = dict(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        cold_wall_ms=10.0,
        warm_wall_ms=8.0,
        hot_wall_ms=7.0,
        cold_ttft_ms=10.0,
        warm_ttft_ms=8.0,
        hot_ttft_ms=7.0,
        cold_e2e_ms=200.0,
        warm_e2e_ms=150.0,
        hot_e2e_ms=120.0,
        n_gen_wall_ok=10,
        n_fix=0,
    )
    assert decide_fastreal(fastreal_stats(**base)) == "KILL"
    base["n_false_hit"] = 0
    base["n_true_hit"] = 10
    base["n_gen_wall_ok"] = 9
    assert decide_fastreal(fastreal_stats(**base)) == "KILL"
