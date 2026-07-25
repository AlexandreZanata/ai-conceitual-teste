"""Contract: H-GRAPHF dual gate vs H-FLAYB."""

from __future__ import annotations

from graphf_ops import GRAPHF_CHUNK, decide_hgraphf


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 40.0}
    stats = {"H-FLAYB": tip}
    assert decide_hgraphf(
        {"mean_lp": -16.02, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hgraphf(
        {"mean_lp": -16.2, "mean_wall": 10.0}, stats
    )
    assert "wall win" in decide_hgraphf(
        {"mean_lp": -16.0, "mean_wall": 50.0}, stats
    )
    assert decide_hgraphf({"mean_lp": -16.0, "mean_wall": 10.0}, {}).startswith(
        "needs H-FLAYB"
    )


def test_given_chunk_when_graphf_then_matches_flayb() -> None:
    assert GRAPHF_CHUNK == 256
