"""Contract: H-ETRAIN dual gate vs H-STAG + e2e wall helper."""

from __future__ import annotations

from etrain_ops import decide_hetrain, e2e_wall_s


def test_given_cache_and_train_when_e2e_then_sum() -> None:
    assert e2e_wall_s(cache_build_s=1.5, train_wall_s=0.5) == 2.0
    assert e2e_wall_s(cache_build_s=0.0, train_wall_s=3.0) == 3.0


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_e2e": 10.0}
    stats = {"H-STAG": tip}
    assert decide_hetrain(
        {"mean_lp": -16.02, "mean_e2e": 8.0}, stats
    ).startswith("PROMOTE")
    assert "quality drop" in decide_hetrain(
        {"mean_lp": -16.2, "mean_e2e": 7.0}, stats
    )
    assert "end-to-end" in decide_hetrain(
        {"mean_lp": -16.0, "mean_e2e": 10.0}, stats
    )
    assert decide_hetrain({"mean_lp": -16.0, "mean_e2e": 8.0}, {}).startswith(
        "needs H-STAG"
    )
