"""Contract: H-PACK dual serving packs vs H-EARLY."""

from __future__ import annotations

from pack_ops import decide_hpack


def test_given_both_packs_when_decide_then_promote() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0}
    serve = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2800.0}
    sroute = {"mean_lp": -12.5, "mean_wall": 6.0, "mean_tps": 5000.0}
    assert decide_hpack(
        {"H-EARLY": early, "H-SERVE": serve, "H-SROUTE": sroute}
    ).startswith("PROMOTE")


def test_given_serve_lp_drift_when_decide_then_kill() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0}
    serve = {"mean_lp": -13.0, "mean_wall": 3.0, "mean_tps": 2800.0}
    sroute = {"mean_lp": -12.5, "mean_wall": 6.0, "mean_tps": 5000.0}
    assert "SERVE lp" in decide_hpack(
        {"H-EARLY": early, "H-SERVE": serve, "H-SROUTE": sroute}
    )


def test_given_sroute_quality_drop_when_decide_then_kill() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0}
    serve = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2800.0}
    sroute = {"mean_lp": -14.2, "mean_wall": 6.0, "mean_tps": 5000.0}
    assert "SROUTE quality" in decide_hpack(
        {"H-EARLY": early, "H-SERVE": serve, "H-SROUTE": sroute}
    )


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_hpack({}).startswith("needs H-EARLY")
