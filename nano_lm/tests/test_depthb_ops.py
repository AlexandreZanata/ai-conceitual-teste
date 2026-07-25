"""Contract: H-DEPTHB dual gate vs H-LAYB (wall|GFLOPs + |Δlp|≤ε)."""

from __future__ import annotations

from depthb_ops import DEPTHB_CHUNK, decide_hdepthb


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 40.0, "mean_gflops": 10.0}
    stats = {"H-LAYB": tip}
    assert decide_hdepthb(
        {"mean_lp": -16.02, "mean_wall": 30.0, "mean_gflops": 10.0}, stats
    ).startswith("PROMOTE")
    assert decide_hdepthb(
        {"mean_lp": -16.0, "mean_wall": 40.0, "mean_gflops": 5.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hdepthb(
        {"mean_lp": -16.2, "mean_wall": 10.0, "mean_gflops": 1.0}, stats
    )
    assert "wall/gflops" in decide_hdepthb(
        {"mean_lp": -16.0, "mean_wall": 50.0, "mean_gflops": 12.0}, stats
    )
    assert decide_hdepthb(
        {"mean_lp": -16.0, "mean_wall": 10.0, "mean_gflops": 1.0}, {}
    ).startswith("needs H-LAYB")


def test_given_chunk_when_depthb_then_matches_layb() -> None:
    assert DEPTHB_CHUNK == 256
