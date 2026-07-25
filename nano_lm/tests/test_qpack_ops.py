"""Contract: H-QPACK FLAYB vs H-POOL quality pack gate."""

from __future__ import annotations

from qpack_ops import decide_hqpack


def test_given_quality_and_speed_when_decide_then_promote() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 20.0, "mean_tps": 800.0}
    flayb = {"mean_lp": -11.9, "mean_wall": 5.0, "mean_tps": 4000.0}
    assert decide_hqpack(flayb, {"H-POOL": tip}).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 20.0, "mean_tps": 800.0}
    flayb = {"mean_lp": -12.2, "mean_wall": 5.0, "mean_tps": 4000.0}
    assert "quality drop" in decide_hqpack(flayb, {"H-POOL": tip})


def test_given_no_speed_win_when_decide_then_kill() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 5.0, "mean_tps": 4000.0}
    flayb = {"mean_lp": -11.9, "mean_wall": 6.0, "mean_tps": 3000.0}
    assert "no wall/tok/s" in decide_hqpack(flayb, {"H-POOL": tip})


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_hqpack(
        {"mean_lp": -12.0, "mean_wall": 5.0, "mean_tps": 1.0}, {}
    ).startswith("needs H-POOL")
