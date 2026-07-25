"""Contract: H-ROUTE dual gate vs GALL/GRAPHF single arms."""

from __future__ import annotations

from route_ops import arm_dominates, decide_hroute


def test_given_arm_when_dominates_then_true_or_false() -> None:
    route = {"mean_lp": -12.0, "mean_wall": 10.0}
    assert arm_dominates({"mean_lp": -11.9, "mean_wall": 9.0}, route)
    assert not arm_dominates({"mean_lp": -12.2, "mean_wall": 9.0}, route)
    assert not arm_dominates({"mean_lp": -11.9, "mean_wall": 11.0}, route)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    gall = {"mean_lp": -12.5, "mean_wall": 8.0}
    graphf = {"mean_lp": -10.5, "mean_wall": 19.0}
    stats = {"H-GALL": gall, "H-GRAPHF": graphf}
    # Tradeoff: better lp than GALL, better wall than GRAPHF → not dominated.
    assert decide_hroute(
        {"mean_lp": -10.9, "mean_wall": 13.0}, stats
    ).startswith("PROMOTE")
    assert "dominated by H-GALL" in decide_hroute(
        {"mean_lp": -12.5, "mean_wall": 9.0}, stats
    )
    assert "dominated by H-GRAPHF" in decide_hroute(
        {"mean_lp": -10.6, "mean_wall": 20.0}, stats
    )
    assert decide_hroute({"mean_lp": -12.0, "mean_wall": 7.0}, {}).startswith(
        "needs H-GALL"
    )
