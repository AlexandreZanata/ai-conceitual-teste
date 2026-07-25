"""Contract: H-XFER transfer dual-gate aggregate."""

from __future__ import annotations

from xfer_ops import decide_hxfer, verdict_pack, verdict_qpack, verdict_tpack


def _promote_all() -> dict[str, dict[str, str]]:
    return {
        "H-PACK": {
            "heldout": "PROMOTE (x)",
            "elongated": "PROMOTE (y)",
            "ood": "PROMOTE (z)",
        },
        "H-QPACK": {
            "heldout": "PROMOTE (x)",
            "elongated": "PROMOTE (y)",
            "ood": "PROMOTE (z)",
        },
        "H-TPACK": {
            "heldout": "PROMOTE (x)",
            "elongated": "PROMOTE (y)",
            "ood": "PROMOTE (z)",
        },
    }


def test_given_all_promote_when_decide_then_promote() -> None:
    assert decide_hxfer(_promote_all()).startswith("PROMOTE")


def test_given_one_kill_when_decide_then_kill_names_slot() -> None:
    v = _promote_all()
    v["H-QPACK"]["ood"] = "KILL (FLAYB no wall/tok/s win vs H-POOL)"
    out = decide_hxfer(v)
    assert out.startswith("KILL")
    assert "H-QPACK/ood" in out


def test_given_missing_recipe_when_decide_then_needs() -> None:
    assert decide_hxfer({}).startswith("needs H-PACK")


def test_given_pack_stats_when_verdict_then_delegates() -> None:
    early = {"mean_lp": -14.0, "mean_wall": 12.0, "mean_tps": 700.0}
    serve = {"mean_lp": -14.0, "mean_wall": 3.0, "mean_tps": 2800.0}
    sroute = {"mean_lp": -12.5, "mean_wall": 6.0, "mean_tps": 5000.0}
    assert verdict_pack(
        {"H-EARLY": early, "H-SERVE": serve, "H-SROUTE": sroute}
    ).startswith("PROMOTE")


def test_given_qpack_stats_when_verdict_then_delegates() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 20.0, "mean_tps": 800.0}
    flayb = {"mean_lp": -11.9, "mean_wall": 5.0, "mean_tps": 4000.0}
    assert verdict_qpack({"H-POOL": tip, "H-FLAYB": flayb}).startswith("PROMOTE")


def test_given_tpack_stats_when_verdict_then_delegates() -> None:
    tip = {"mean_lp": -13.0, "mean_ms_step": 19.0}
    s = {"mean_lp": -12.5, "mean_ms_step": 14.0}
    assert verdict_tpack({"H-STAG": tip, "H-TPACK": s}).startswith("PROMOTE")
