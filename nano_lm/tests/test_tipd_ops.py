"""Contract: H-TIPD tip-replacement dual gate (capacity + no serve regress)."""

from __future__ import annotations

from tipd_ops import decide_htipd, serve_regresses, tip_outcome


def test_given_capacity_and_serve_hold_when_decide_then_promote() -> None:
    out = decide_htipd(
        retip_lp=-12.0,
        control_lp=-13.0,
        early_retip={"mean_lp": -11.5, "mean_wall": 8.0},
        early_control={"mean_lp": -11.6, "mean_wall": 20.0},
        pool_retip={"mean_lp": -11.4, "mean_wall": 9.0},
        pool_control={"mean_lp": -11.5, "mean_wall": 22.0},
    )
    assert out.startswith("PROMOTE")
    assert tip_outcome(out) == "STAG_PRIME"


def test_given_serve_only_win_when_decide_then_kill_capacity() -> None:
    """RETIP may PROMOTE on serve alone; TIPD requires tip capacity."""
    out = decide_htipd(
        retip_lp=-13.5,
        control_lp=-13.0,
        early_retip={"mean_lp": -11.0, "mean_wall": 5.0},
        early_control={"mean_lp": -12.0, "mean_wall": 20.0},
        pool_retip={"mean_lp": -11.0, "mean_wall": 5.0},
        pool_control={"mean_lp": -12.0, "mean_wall": 20.0},
    )
    assert out.startswith("KILL")
    assert "STAG′ ≤ STAG" in out
    assert tip_outcome(out) == "UTIL"


def test_given_capacity_but_early_regress_when_decide_then_kill() -> None:
    out = decide_htipd(
        retip_lp=-12.0,
        control_lp=-13.0,
        early_retip={"mean_lp": -12.2, "mean_wall": 5.0},
        early_control={"mean_lp": -12.0, "mean_wall": 10.0},
        pool_retip={"mean_lp": -11.5, "mean_wall": 9.0},
        pool_control={"mean_lp": -11.5, "mean_wall": 22.0},
    )
    assert out.startswith("KILL")
    assert "EARLY serve regresses" in out


def test_given_capacity_but_pool_regress_when_decide_then_kill() -> None:
    out = decide_htipd(
        retip_lp=-12.0,
        control_lp=-13.0,
        early_retip={"mean_lp": -11.5, "mean_wall": 8.0},
        early_control={"mean_lp": -11.6, "mean_wall": 20.0},
        pool_retip={"mean_lp": -12.2, "mean_wall": 5.0},
        pool_control={"mean_lp": -12.0, "mean_wall": 10.0},
    )
    assert out.startswith("KILL")
    assert "POOL serve regresses" in out


def test_given_equal_lp_when_decide_then_kill() -> None:
    out = decide_htipd(
        retip_lp=-13.0,
        control_lp=-13.0,
        early_retip={"mean_lp": -11.5, "mean_wall": 8.0},
        early_control={"mean_lp": -11.6, "mean_wall": 20.0},
        pool_retip={"mean_lp": -11.4, "mean_wall": 9.0},
        pool_control={"mean_lp": -11.5, "mean_wall": 22.0},
    )
    assert out.startswith("KILL")


def test_given_lp_within_eps_when_serve_regresses_then_false() -> None:
    assert not serve_regresses(
        {"mean_lp": -12.04, "mean_wall": 10.0},
        {"mean_lp": -12.0, "mean_wall": 10.0},
    )


def test_given_missing_early_when_decide_then_needs() -> None:
    out = decide_htipd(
        retip_lp=-12.0,
        control_lp=-13.0,
        early_retip=None,
        early_control=None,
        pool_retip={"mean_lp": -11.4, "mean_wall": 9.0},
        pool_control={"mean_lp": -11.5, "mean_wall": 22.0},
    )
    assert out.startswith("needs EARLY")
