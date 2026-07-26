"""Contract: H-SCORERAM pack cache persist + warm gate."""

from __future__ import annotations

from pathlib import Path

from scoreram_ops import MIN_HIT_RATE, PackScoreCache, decide_hscoreram


def test_given_cache_when_save_load_then_prime_hits(tmp_path: Path) -> None:
    # GIVEN filled cache WHEN save+load THEN warm get hits
    cold = PackScoreCache()
    cold.get_or_compute("story", "p", "c", lambda: -4.0)
    path = tmp_path / "cache.json"
    cold.save(path)
    warm = PackScoreCache.load(path)
    assert warm.size() == 1
    calls = {"n": 0}

    def boom() -> float:
        calls["n"] += 1
        return 0.0

    assert warm.get_or_compute("story", "p", "c", boom) == -4.0
    assert calls["n"] == 0
    assert warm.hits == 1
    assert warm.forwards == 0


def test_given_warm_wall_down_lp_same_when_decide_then_promote() -> None:
    d = decide_hscoreram(
        cold_wall=100.0,
        warm_wall=40.0,
        cold_story=-10.0,
        warm_story=-10.0,
        cold_code=-12.0,
        warm_code=-12.0,
        hit_rate=0.9,
    )
    assert d.startswith("PROMOTE")
    assert "SCORERAM" in d
    assert "hit_rate" in d


def test_given_lp_drift_when_decide_then_kill() -> None:
    d = decide_hscoreram(
        cold_wall=100.0,
        warm_wall=40.0,
        cold_story=-10.0,
        warm_story=-10.2,
        cold_code=-12.0,
        warm_code=-12.0,
        hit_rate=0.9,
    )
    assert d.startswith("KILL")
    assert "story_lp" in d


def test_given_warm_not_faster_when_decide_then_kill() -> None:
    d = decide_hscoreram(
        cold_wall=40.0,
        warm_wall=40.0,
        cold_story=-10.0,
        warm_story=-10.0,
        cold_code=-12.0,
        warm_code=-12.0,
        hit_rate=0.9,
    )
    assert d.startswith("KILL")
    assert "wall" in d.lower()


def test_given_low_hit_rate_when_decide_then_kill() -> None:
    d = decide_hscoreram(
        cold_wall=100.0,
        warm_wall=40.0,
        cold_story=-10.0,
        warm_story=-10.0,
        cold_code=-12.0,
        warm_code=-12.0,
        hit_rate=MIN_HIT_RATE - 0.01,
    )
    assert d.startswith("KILL")
    assert "hit_rate" in d
