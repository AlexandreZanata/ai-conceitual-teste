"""Contract: H-TPACK PRE3 ms/step vs live H-STAG (not e2e)."""

from __future__ import annotations

from tpack_ops import decide_htpack


def test_given_ms_step_win_when_decide_then_promote() -> None:
    tip = {"mean_lp": -13.0, "mean_ms_step": 19.0}
    s = {"mean_lp": -12.5, "mean_ms_step": 14.0}
    assert decide_htpack(s, {"H-STAG": tip}).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill() -> None:
    tip = {"mean_lp": -13.0, "mean_ms_step": 19.0}
    s = {"mean_lp": -13.2, "mean_ms_step": 14.0}
    assert "quality drop" in decide_htpack(s, {"H-STAG": tip})


def test_given_no_ms_step_win_when_decide_then_kill() -> None:
    tip = {"mean_lp": -13.0, "mean_ms_step": 14.0}
    s = {"mean_lp": -12.5, "mean_ms_step": 15.0}
    assert "step-time" in decide_htpack(s, {"H-STAG": tip})


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_htpack({"mean_lp": -12.0, "mean_ms_step": 1.0}, {}).startswith(
        "needs H-STAG"
    )
