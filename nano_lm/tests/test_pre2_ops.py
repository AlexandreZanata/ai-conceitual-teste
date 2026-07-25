"""Contract: H-PRE2 dual gate vs H-ADAMF."""

from __future__ import annotations

from pre2_ops import decide_hpre2


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 10.0}
    stats = {"H-ADAMF": tip}
    assert decide_hpre2(
        {"mean_lp": -16.02, "mean_ms_step": 8.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hpre2(
        {"mean_lp": -16.2, "mean_ms_step": 7.0}, stats
    )
    assert "step-time" in decide_hpre2(
        {"mean_lp": -16.0, "mean_ms_step": 10.0}, stats
    )
    assert decide_hpre2({"mean_lp": -16.0, "mean_ms_step": 8.0}, {}).startswith(
        "needs H-ADAMF"
    )
