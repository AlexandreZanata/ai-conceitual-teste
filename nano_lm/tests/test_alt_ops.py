"""Contract: H-ALT shallow schedule + dual gate vs EARLY."""

from __future__ import annotations

from alt_ops import clamp_alt_gene, decide_halt, use_shallow_step


def test_given_period_when_schedule_then_alternate() -> None:
    # start full: steps 0,1 full; 2,3 shallow for period=2
    assert use_shallow_step(step=0, period=2, start_shallow=False) is False
    assert use_shallow_step(step=1, period=2, start_shallow=False) is False
    assert use_shallow_step(step=2, period=2, start_shallow=False) is True
    assert use_shallow_step(step=3, period=2, start_shallow=False) is True
    assert use_shallow_step(step=0, period=1, start_shallow=True) is True
    assert use_shallow_step(step=1, period=1, start_shallow=True) is False


def test_given_tip_when_clamp_then_codebook() -> None:
    tip = {
        "n": 1,
        "temperature": 0.8,
        "top_p": 0.9,
        "min_new": 8,
        "patience": 2,
        "conf_threshold": 0.7,
    }
    g = clamp_alt_gene(
        {"alt_period": 3, "shallow_skip": 9, "start_shallow": 1}, tip
    )
    assert g["alt_period"] == 2
    assert g["shallow_skip"] == 1
    assert g["start_shallow"] == 1
    assert g["min_new"] == 8


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0, "mean_gflops": 10.0}
    stats = {"H-EARLY": tip}
    assert decide_halt(
        {"mean_lp": -16.0, "mean_wall": 60.0, "mean_gflops": 10.0}, stats
    ).startswith("PROMOTE")
    assert decide_halt(
        {"mean_lp": -16.0, "mean_wall": 70.0, "mean_gflops": 8.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_halt(
        {"mean_lp": -16.2, "mean_wall": 50.0, "mean_gflops": 5.0}, stats
    )
    assert "wall/GFLOPs" in decide_halt(
        {"mean_lp": -15.9, "mean_wall": 70.0, "mean_gflops": 10.0}, stats
    )
