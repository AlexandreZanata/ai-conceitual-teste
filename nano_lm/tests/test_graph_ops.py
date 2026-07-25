"""Contract: H-GRAPH dual gate vs H-LAYB + capture helper on CUDA-only."""

from __future__ import annotations

from graph_ops import GRAPH_CHUNK, decide_hgraph


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 40.0}
    stats = {"H-LAYB": tip}
    assert decide_hgraph(
        {"mean_lp": -16.02, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hgraph(
        {"mean_lp": -16.2, "mean_wall": 10.0}, stats
    )
    assert "wall win" in decide_hgraph(
        {"mean_lp": -16.0, "mean_wall": 50.0}, stats
    )
    assert decide_hgraph({"mean_lp": -16.0, "mean_wall": 10.0}, {}).startswith(
        "needs H-LAYB"
    )


def test_given_chunk_when_graph_then_matches_layb() -> None:
    assert GRAPH_CHUNK == 256
