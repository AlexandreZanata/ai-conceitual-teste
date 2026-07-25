"""Contract: H-SKIP vs H-BAT wall/tps + GFLOPs honesty."""

from __future__ import annotations

from skip_ops import decide_hskip, gflops_beyond_tip


def test_given_gflops_when_beyond_then_true_or_false() -> None:
    tip = {"mean_gflops": 10.0}
    assert gflops_beyond_tip({"mean_gflops": 11.0}, tip)
    assert not gflops_beyond_tip({"mean_gflops": 10.2}, tip)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    bat = {"mean_wall": 10.0, "mean_tps": 1000.0, "mean_gflops": 7.0}
    stats = {"H-BAT": bat}
    assert decide_hskip(
        {"mean_wall": 5.0, "mean_tps": 2000.0, "mean_gflops": 7.0}, stats
    ).startswith("PROMOTE")
    assert "no wall/tok/s" in decide_hskip(
        {"mean_wall": 11.0, "mean_tps": 900.0, "mean_gflops": 7.0}, stats
    )
    assert "GFLOPs" in decide_hskip(
        {"mean_wall": 5.0, "mean_tps": 2000.0, "mean_gflops": 9.0}, stats
    )
    assert decide_hskip(
        {"mean_wall": 5.0, "mean_tps": 2000.0, "mean_gflops": 7.0}, {}
    ).startswith("needs H-BAT")
