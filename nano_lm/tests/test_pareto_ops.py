"""Contract: H-PARETO efficiency inflate flag + audit decide."""

from __future__ import annotations

from pareto_ops import classify_util, decide_hpareto, is_efficiency_inflated


def test_given_tps_up_gflops_up_when_inflate_then_true() -> None:
    tip = {"mean_tps": 1000.0, "mean_gflops": 10.0}
    util = {"mean_tps": 2000.0, "mean_gflops": 12.0}  # +20% gf
    assert is_efficiency_inflated(util, tip)
    assert classify_util(util, tip).startswith("FLAG")


def test_given_tps_up_gflops_tie_when_inflate_then_false() -> None:
    tip = {"mean_tps": 1000.0, "mean_gflops": 10.0}
    util = {"mean_tps": 2000.0, "mean_gflops": 10.2}  # +2% < 5% δ
    assert not is_efficiency_inflated(util, tip)
    assert classify_util(util, tip).startswith("KEEP")


def test_given_tps_down_when_inflate_then_false() -> None:
    tip = {"mean_tps": 2000.0, "mean_gflops": 10.0}
    util = {"mean_tps": 1500.0, "mean_gflops": 20.0}
    assert not is_efficiency_inflated(util, tip)


def test_given_pairs_when_decide_then_promote_or_kill() -> None:
    assert decide_hpareto(n_pairs=0, n_flagged=0).startswith("KILL")
    assert decide_hpareto(n_pairs=3, n_flagged=1).startswith("PROMOTE")
    assert "1 flagged" in decide_hpareto(n_pairs=3, n_flagged=1)
