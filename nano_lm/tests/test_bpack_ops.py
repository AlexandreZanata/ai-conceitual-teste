"""Contract: H-BPACK SKIP+LAYB packs vs H-EARLY."""

from __future__ import annotations

from bpack_ops import decide_hbpack


def test_given_both_packs_when_decide_then_promote() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0, "mean_gflops": 7.0}
    skip = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2500.0, "mean_gflops": 7.0}
    layb = {"mean_lp": -14.0, "mean_wall": 2.0, "mean_tps": 4000.0, "mean_gflops": 7.0}
    assert decide_hbpack(
        {"H-EARLY": early, "H-SKIP": skip, "H-LAYB": layb}
    ).startswith("PROMOTE")


def test_given_skip_gflops_inflate_when_decide_then_kill() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0, "mean_gflops": 7.0}
    skip = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2500.0, "mean_gflops": 10.0}
    layb = {"mean_lp": -14.0, "mean_wall": 2.0, "mean_tps": 4000.0, "mean_gflops": 7.0}
    assert "SKIP GFLOPs" in decide_hbpack(
        {"H-EARLY": early, "H-SKIP": skip, "H-LAYB": layb}
    )


def test_given_layb_no_win_when_decide_then_kill() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0, "mean_gflops": 7.0}
    skip = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2500.0, "mean_gflops": 7.0}
    layb = {"mean_lp": -14.0, "mean_wall": 13.0, "mean_tps": 600.0, "mean_gflops": 7.0}
    assert "LAYB no wall" in decide_hbpack(
        {"H-EARLY": early, "H-SKIP": skip, "H-LAYB": layb}
    )


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_hbpack({}).startswith("needs H-EARLY")
