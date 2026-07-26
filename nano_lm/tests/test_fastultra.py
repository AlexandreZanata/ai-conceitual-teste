"""Contract: Wave AF3 H-FASTULTRA — wall/TTFT/e2e ↓ vs FASTMAX baseline."""

from __future__ import annotations

from askfast_ops import AskCompletionCache, WALL_DROP_MIN
from fastultra_ops import (
    FASTMAX_HOT_E2E_MS,
    FASTMAX_WARM_E2E_MS,
    FASTULTRA_ID,
    FASTULTRA_N,
    HOT_ROUNDS,
    WARMUP_ROUNDS,
    decide_fastultra,
    fastultra_stats,
    mean_ms,
    score_fastultra_trial,
    ttft_of,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF3 H-FASTULTRA
    assert FASTULTRA_ID == "H-FASTULTRA"
    assert FASTULTRA_N == 10
    assert WALL_DROP_MIN == 0.20
    assert HOT_ROUNDS == 48
    assert WARMUP_ROUNDS == 8
    assert HOT_ROUNDS > 12
    assert FASTMAX_HOT_E2E_MS == 0.034374999813735485
    assert FASTMAX_WARM_E2E_MS == 0.49394100096833427


def test_given_payload_when_ttft_then_prefer_explicit() -> None:
    assert ttft_of({"ttft_ms": 1.5, "wall_ms": 9.0}) == 1.5
    assert ttft_of({"wall_ms": 3.0}) == 3.0


def test_given_values_when_mean_then_average() -> None:
    assert mean_ms([10.0, 20.0]) == 15.0
    assert mean_ms([]) == 0.0


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_fastultra_trial(
        mode="ASKFAST_CACHE",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
    )
    assert score == 9.0 and err is False
    assert any("FASTULTRA" in n for n in notes)


def test_given_cache_when_peek_key_then_no_counter_bump() -> None:
    cache = AskCompletionCache()
    cache.put("What is a BIP?", {"completion": "Bitcoin Improvement Proposal"})
    from z_wrap import normalize_question

    key = normalize_question("What is a BIP?")
    hit = cache.peek_key(key)
    assert hit is not None
    assert hit["mode"] == "ASKFAST_CACHE"
    assert hit["wall_ms"] == 0.0
    assert cache.hits == 0 and cache.misses == 0


def test_given_hot_e2e_faster_when_decide_then_promote() -> None:
    stats = fastultra_stats(
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
        hot_e2e_ms=0.02,  # < FASTMAX hot e2e
        cache_hit_rate=0.66,
    )
    assert stats["pass_e2e_vs_fastmax"] is True
    assert decide_fastultra(stats) == "PROMOTE"


def test_given_quality_no_speed_when_decide_then_hold() -> None:
    stats = fastultra_stats(
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
    assert decide_fastultra(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = fastultra_stats(
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
        hot_e2e_ms=0.01,
        cache_hit_rate=1.0,
    )
    assert decide_fastultra(stats) == "KILL"
