"""Contract: H-SOFT ms/step helper + dual gate vs live STAG."""

from __future__ import annotations

from soft_ops import decide_hsoft, ms_per_step


def test_given_wall_when_ms_per_step_then_ratio() -> None:
    assert ms_per_step(wall_s=1.5, steps=30) == 50.0
    assert ms_per_step(wall_s=1.0, steps=0) == 0.0


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 40.0}
    stats = {"H-STAG": tip}
    assert decide_hsoft(
        {"mean_lp": -16.0, "mean_ms_step": 25.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hsoft(
        {"mean_lp": -16.2, "mean_ms_step": 20.0}, stats
    )
    assert "step-time" in decide_hsoft(
        {"mean_lp": -15.9, "mean_ms_step": 40.0}, stats
    )
