"""Contract: Wave AC3 H-FASTPLUS — wall/TTFT/e2e ↓ vs AB ask baseline."""

from __future__ import annotations

from askfast_ops import WALL_DROP_MIN
from fastplus_ops import (
    AB_ASKFAST_E2E_MS,
    AB_ASKFAST_MEAN_WALL_MS,
    AB_OPEN_MEAN_WALL_MS,
    FASTPLUS_ID,
    FASTPLUS_N,
    decide_fastplus,
    fastplus_stats,
    mean_ms,
    score_fastplus_trial,
    ttft_of,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.5 / §12.1 AC3 H-FASTPLUS
    assert FASTPLUS_ID == "H-FASTPLUS"
    assert FASTPLUS_N == 10
    assert WALL_DROP_MIN == 0.20
    assert AB_ASKFAST_MEAN_WALL_MS == 0.0
    assert AB_OPEN_MEAN_WALL_MS == 25.17925870010913
    assert AB_ASKFAST_E2E_MS == 88.75692499987053


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0


def test_given_values_when_mean_then_average() -> None:
    assert mean_ms([10.0, 20.0]) == 15.0
    assert mean_ms([]) == 0.0


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_fastplus_trial(
        mode="ASKFAST_CACHE",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
    )
    assert score == 9.0 and err is False
    assert any("FASTPLUS" in n for n in notes)


def test_given_speed_and_quality_when_decide_then_promote() -> None:
    stats = fastplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        cold_wall_ms=0.0,
        warm_wall_ms=0.0,
        cold_ttft_ms=0.0,
        warm_ttft_ms=0.0,
        cold_e2e_ms=50.0,
        warm_e2e_ms=40.0,  # < AB e2e
        cache_hit_rate=0.5,
    )
    assert stats["pass_speed"] is True
    assert decide_fastplus(stats) == "PROMOTE"


def test_given_quality_no_speed_when_decide_then_hold() -> None:
    # Cold wall worse than AB open; warm e2e slower than AB; warm ttft not down.
    stats = fastplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        cold_wall_ms=30.0,
        warm_wall_ms=0.0,
        cold_ttft_ms=30.0,
        warm_ttft_ms=0.0,
        cold_e2e_ms=200.0,
        warm_e2e_ms=200.0,
        cache_hit_rate=0.5,
    )
    # warm_wall == AB askfast 0 → wall_down False via askfast;
    # drop vs open: (25.17-30)/25 < 0 → 0, pass_wall False;
    # ttft_down: warm==0 and cold < open? 30 < 25? no → False
    # e2e_down: 200 < 88? no
    assert stats["pass_speed"] is False
    assert decide_fastplus(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastplus_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        cold_wall_ms=0.0,
        warm_wall_ms=0.0,
        cold_ttft_ms=0.0,
        warm_ttft_ms=0.0,
        cold_e2e_ms=10.0,
        warm_e2e_ms=5.0,
        cache_hit_rate=1.0,
    )
    assert decide_fastplus(stats) == "KILL"
