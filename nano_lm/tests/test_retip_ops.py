"""Contract: H-RETIP capacity OR serve-win dual gate."""

from __future__ import annotations

from retip_ops import capacity_win, decide_hretip, serve_win


def test_given_capacity_when_decide_then_promote() -> None:
    out = decide_hretip(
        retip_lp=-12.0,
        control_lp=-13.0,
        early_retip={"mean_lp": -14.0, "mean_wall": 20.0},
        early_control={"mean_lp": -12.0, "mean_wall": 10.0},
        pool_retip={"mean_lp": -14.0, "mean_wall": 20.0},
        pool_control={"mean_lp": -12.0, "mean_wall": 10.0},
    )
    assert out.startswith("PROMOTE")
    assert "capacity" in out


def test_given_early_serve_when_decide_then_promote() -> None:
    out = decide_hretip(
        retip_lp=-13.0,
        control_lp=-12.5,
        early_retip={"mean_lp": -11.5, "mean_wall": 8.0},
        early_control={"mean_lp": -11.6, "mean_wall": 20.0},
        pool_retip={"mean_lp": -14.0, "mean_wall": 20.0},
        pool_control={"mean_lp": -12.0, "mean_wall": 10.0},
    )
    assert out.startswith("PROMOTE")
    assert "EARLY-serve" in out


def test_given_no_capacity_no_serve_when_decide_then_kill() -> None:
    out = decide_hretip(
        retip_lp=-13.5,
        control_lp=-13.0,
        early_retip={"mean_lp": -12.5, "mean_wall": 25.0},
        early_control={"mean_lp": -12.0, "mean_wall": 20.0},
        pool_retip={"mean_lp": -12.5, "mean_wall": 25.0},
        pool_control={"mean_lp": -12.0, "mean_wall": 20.0},
    )
    assert out.startswith("KILL")


def test_given_equal_lp_when_capacity_then_false() -> None:
    assert not capacity_win(-13.0, -13.0)


def test_given_wall_win_when_serve_then_true() -> None:
    assert serve_win(
        {"mean_lp": -12.0, "mean_wall": 5.0},
        {"mean_lp": -12.0, "mean_wall": 10.0},
    )


def test_given_quality_drop_when_serve_then_false() -> None:
    assert not serve_win(
        {"mean_lp": -12.2, "mean_wall": 5.0},
        {"mean_lp": -12.0, "mean_wall": 10.0},
    )
