"""Contract: H-PINC dual gate vs H-PIN + compiled train flag."""

from __future__ import annotations

from pinc_ops import decide_hpinc


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 10.0}
    stats = {"H-PIN": tip}
    assert decide_hpinc(
        {"mean_lp": -16.02, "mean_ms_step": 8.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hpinc(
        {"mean_lp": -16.2, "mean_ms_step": 7.0}, stats
    )
    assert "step-time" in decide_hpinc(
        {"mean_lp": -16.0, "mean_ms_step": 10.0}, stats
    )


def test_given_missing_tip_when_decide_then_needs() -> None:
    assert decide_hpinc({"mean_lp": -1.0, "mean_ms_step": 1.0}, {}).startswith(
        "needs H-PIN"
    )
