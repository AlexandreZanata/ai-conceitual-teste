"""Contract: Wave AE3 H-FASTMAX — wall/TTFT/e2e ↓ vs FASTPLUS baseline."""

from __future__ import annotations

from askfast_ops import WALL_DROP_MIN
from fastmax_ops import (
    FASTMAX_ID,
    FASTMAX_N,
    FASTPLUS_COLD_E2E_MS,
    FASTPLUS_WARM_E2E_MS,
    FASTPLUS_WARM_WALL_MS,
    decide_fastmax,
    fastmax_stats,
    mean_ms,
    score_fastmax_trial,
    ttft_of,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE3 H-FASTMAX
    assert FASTMAX_ID == "H-FASTMAX"
    assert FASTMAX_N == 10
    assert WALL_DROP_MIN == 0.20
    assert FASTPLUS_WARM_WALL_MS == 0.0
    assert FASTPLUS_WARM_E2E_MS == 0.2903160002460936
    assert FASTPLUS_COLD_E2E_MS == 1.0746810003183782


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0


def test_given_values_when_mean_then_average() -> None:
    assert mean_ms([10.0, 20.0]) == 15.0
    assert mean_ms([]) == 0.0


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_fastmax_trial(
        mode="ASKFAST_CACHE",
        completion="xprv / xpub",
        expected_gold="xprv / xpub",
        lookup_kind="TRUE_HIT",
    )
    assert score == 9.0 and err is False
    assert any("FASTMAX" in n for n in notes)


def test_given_hot_e2e_faster_when_decide_then_promote() -> None:
    stats = fastmax_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        cold_wall_ms=0.0,
        warm_wall_ms=0.0,
        hot_wall_ms=0.0,
        cold_ttft_ms=0.0,
        warm_ttft_ms=0.0,
        hot_ttft_ms=0.0,
        cold_e2e_ms=1.0,
        warm_e2e_ms=0.4,
        hot_e2e_ms=0.1,  # < FASTPLUS warm e2e
        cache_hit_rate=0.66,
    )
    assert stats["pass_e2e_vs_fastplus"] is True
    assert decide_fastmax(stats) == "PROMOTE"


def test_given_quality_no_speed_when_decide_then_hold() -> None:
    stats = fastmax_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        cold_wall_ms=30.0,
        warm_wall_ms=0.0,
        hot_wall_ms=0.0,
        cold_ttft_ms=30.0,
        warm_ttft_ms=0.0,
        hot_ttft_ms=0.0,
        cold_e2e_ms=200.0,
        warm_e2e_ms=200.0,
        hot_e2e_ms=200.0,
        cache_hit_rate=0.5,
    )
    assert stats["pass_speed"] is False
    assert decide_fastmax(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastmax_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        cold_wall_ms=0.0,
        warm_wall_ms=0.0,
        hot_wall_ms=0.0,
        cold_ttft_ms=0.0,
        warm_ttft_ms=0.0,
        hot_ttft_ms=0.0,
        cold_e2e_ms=10.0,
        warm_e2e_ms=5.0,
        hot_e2e_ms=1.0,
        cache_hit_rate=1.0,
    )
    assert decide_fastmax(stats) == "KILL"
