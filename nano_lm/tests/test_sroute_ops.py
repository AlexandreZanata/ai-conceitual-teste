"""Contract: H-SROUTE vs H-SERVE dominance gate."""

from __future__ import annotations

from sroute_ops import decide_hsroute


def test_given_serve_dominates_when_decide_then_kill() -> None:
    serve = {"mean_lp": -11.0, "mean_wall": 5.0}
    stats = {"H-SERVE": serve}
    assert "dominated by H-SERVE" in decide_hsroute(
        {"mean_lp": -11.1, "mean_wall": 8.0}, stats
    )


def test_given_tradeoff_when_decide_then_promote() -> None:
    serve = {"mean_lp": -13.0, "mean_wall": 3.0}
    stats = {"H-SERVE": serve}
    # Better lp, worse wall → not dominated.
    assert decide_hsroute(
        {"mean_lp": -12.0, "mean_wall": 7.0}, stats
    ).startswith("PROMOTE")


def test_given_missing_serve_when_decide_then_needs_control() -> None:
    assert decide_hsroute({"mean_lp": -12.0, "mean_wall": 5.0}, {}).startswith(
        "needs H-SERVE"
    )
