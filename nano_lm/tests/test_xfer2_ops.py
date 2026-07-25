"""Contract: H-XFER2 PACK-only transfer dual-gate aggregate."""

from __future__ import annotations

from xfer2_ops import decide_hxfer2, verdict_bpack, verdict_pack


def _promote_pack() -> dict[str, dict[str, str]]:
    return {
        "H-PACK": {
            "elongated": "PROMOTE (x)",
            "ood": "PROMOTE (y)",
            "ood_long": "PROMOTE (z)",
        }
    }


def test_given_all_pack_promote_when_decide_then_promote() -> None:
    assert decide_hxfer2(_promote_pack()).startswith("PROMOTE")


def test_given_bpack_kill_when_decide_then_still_promote() -> None:
    v = _promote_pack()
    v["H-BPACK"] = {
        "elongated": "KILL (SKIP no wall/tok/s win vs H-EARLY)",
        "ood": "PROMOTE (x)",
        "ood_long": "PROMOTE (y)",
    }
    assert decide_hxfer2(v).startswith("PROMOTE")


def test_given_pack_ood_kill_when_decide_then_kill_names_slot() -> None:
    v = _promote_pack()
    v["H-PACK"]["ood"] = "KILL (SERVE no wall/tok/s win vs H-EARLY)"
    out = decide_hxfer2(v)
    assert out.startswith("KILL")
    assert "H-PACK/ood" in out


def test_given_missing_pack_when_decide_then_needs() -> None:
    assert decide_hxfer2({}).startswith("needs H-PACK")


def test_given_missing_ood_long_when_decide_then_needs() -> None:
    v = {
        "H-PACK": {
            "elongated": "PROMOTE (x)",
            "ood": "PROMOTE (y)",
        }
    }
    assert decide_hxfer2(v) == "needs H-PACK/ood_long"


def test_given_pack_stats_when_verdict_then_delegates() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0}
    serve = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2800.0}
    sroute = {"mean_lp": -12.5, "mean_wall": 6.0, "mean_tps": 5000.0}
    assert verdict_pack(
        {"H-EARLY": early, "H-SERVE": serve, "H-SROUTE": sroute}
    ).startswith("PROMOTE")


def test_given_bpack_stats_when_verdict_then_delegates() -> None:
    early = {
        "mean_lp": -14.0,
        "mean_wall": 12.0,
        "mean_tps": 700.0,
        "mean_gflops": 10.0,
    }
    skip = {
        "mean_lp": -14.0,
        "mean_wall": 4.0,
        "mean_tps": 2000.0,
        "mean_gflops": 10.0,
    }
    layb = {
        "mean_lp": -14.0,
        "mean_wall": 5.0,
        "mean_tps": 1800.0,
        "mean_gflops": 10.0,
    }
    assert verdict_bpack(
        {"H-EARLY": early, "H-SKIP": skip, "H-LAYB": layb}
    ).startswith("PROMOTE")
