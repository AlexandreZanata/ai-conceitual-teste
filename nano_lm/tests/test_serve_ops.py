"""Contract: H-SERVE dual gate vs H-EARLY + recipe pick."""

from __future__ import annotations

from serve_ops import decide_hserve, pick_serve_recipe


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 60.0, "mean_tps": 1000.0}
    stats = {"H-EARLY": tip}
    assert decide_hserve(
        {"mean_lp": -12.02, "mean_wall": 40.0, "mean_tps": 900.0}, stats
    ).startswith("PROMOTE")
    assert decide_hserve(
        {"mean_lp": -12.0, "mean_wall": 70.0, "mean_tps": 2000.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hserve(
        {"mean_lp": -12.2, "mean_wall": 30.0, "mean_tps": 3000.0}, stats
    )
    assert "wall/tok" in decide_hserve(
        {"mean_lp": -12.0, "mean_wall": 60.0, "mean_tps": 1000.0}, stats
    )
    assert decide_hserve(
        {"mean_lp": -12.0, "mean_wall": 40.0, "mean_tps": 2000.0}, {}
    ).startswith("needs H-EARLY")


def test_given_candidates_when_pick_then_prefer_quality_ok_min_wall() -> None:
    cands = {
        "speed": {"mean_lp": -12.0, "mean_wall_ms": 20.0},
        "quality": {"mean_lp": -12.5, "mean_wall_ms": 10.0},
    }
    assert pick_serve_recipe(cands, early_lp=-12.0) == "speed"
    cands["quality"] = {"mean_lp": -12.02, "mean_wall_ms": 15.0}
    assert pick_serve_recipe(cands, early_lp=-12.0) == "quality"
