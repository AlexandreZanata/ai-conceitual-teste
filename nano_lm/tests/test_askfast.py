"""Contract: Wave AB2 H-ASKFAST — wall↓≥20% vs baseline; quality floor."""

from __future__ import annotations

from askfast_ops import (
    ASKFAST_ID,
    ASKFAST_N,
    WALL_DROP_MIN,
    AskCompletionCache,
    askfast_stats,
    decide_askfast,
    wall_reduction,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.3 AB2 H-ASKFAST
    assert ASKFAST_ID == "H-ASKFAST"
    assert ASKFAST_N == 10
    assert WALL_DROP_MIN == 0.20


def test_given_walls_when_reduction_then_fraction() -> None:
    assert wall_reduction(100.0, 20.0) == 0.8
    assert wall_reduction(100.0, 100.0) == 0.0
    assert wall_reduction(0.0, 0.0) == 1.0


def test_given_cache_when_put_get_then_hit() -> None:
    cache = AskCompletionCache()
    cache.put("What is BIP-39?", {"completion": "mnemonic seed", "mode": "X"})
    hit = cache.get("What is BIP-39?")
    assert hit is not None
    assert hit["completion"] == "mnemonic seed"
    assert hit["mode"] == "ASKFAST_CACHE"
    assert cache.hit_rate() == 1.0
    assert cache.get("unknown?") is None
    assert cache.hits == 1 and cache.misses == 1


def test_given_cache_when_peek_then_no_counter_bump() -> None:
    # GIVEN/WHEN/THEN: FASTMAX hot path peeks without distorting hit_rate
    cache = AskCompletionCache()
    cache.put("q", {"completion": "g", "mode": "X"})
    peeked = cache.peek("q")
    assert peeked is not None and peeked["completion"] == "g"
    assert cache.hits == 0 and cache.misses == 0
    assert cache.peek("missing") is None
    assert cache.hits == 0 and cache.misses == 0


def test_given_wall_and_quality_when_decide_then_promote() -> None:
    stats = askfast_stats(
        [9.0] * 10,
        [False] * 10,
        baseline_wall_ms=50.0,
        askfast_wall_ms=5.0,
        cache_hit_rate=0.5,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
    )
    assert stats["pass_wall"] is True
    assert stats["pass_quality"] is True
    assert decide_askfast(stats) == "PROMOTE"


def test_given_quality_no_wall_when_decide_then_hold() -> None:
    stats = askfast_stats(
        [9.0] * 10,
        [False] * 10,
        baseline_wall_ms=10.0,
        askfast_wall_ms=9.0,  # 10% only
        cache_hit_rate=0.0,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
    )
    assert stats["pass_wall"] is False
    assert decide_askfast(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = askfast_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        baseline_wall_ms=100.0,
        askfast_wall_ms=0.0,
        cache_hit_rate=1.0,
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
    )
    assert decide_askfast(stats) == "KILL"


def test_given_bad_quality_when_decide_then_kill() -> None:
    stats = askfast_stats(
        [4.0] * 10,
        [True] * 10,
        baseline_wall_ms=100.0,
        askfast_wall_ms=0.0,
        cache_hit_rate=0.0,
        n_true_hit=0,
        n_false_hit=0,
        n_miss=10,
    )
    assert decide_askfast(stats) == "KILL"
