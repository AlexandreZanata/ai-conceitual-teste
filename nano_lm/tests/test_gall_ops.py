"""Contract: H-GALL dual gate vs H-GRAPH."""

from __future__ import annotations

from gall_ops import GALL_CHUNK, decide_hgall


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 40.0}
    stats = {"H-GRAPH": tip}
    assert decide_hgall(
        {"mean_lp": -16.02, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hgall(
        {"mean_lp": -16.2, "mean_wall": 10.0}, stats
    )
    assert "wall win" in decide_hgall(
        {"mean_lp": -16.0, "mean_wall": 50.0}, stats
    )
    assert decide_hgall({"mean_lp": -16.0, "mean_wall": 10.0}, {}).startswith(
        "needs H-GRAPH"
    )


def test_given_chunk_when_gall_then_matches_graph() -> None:
    assert GALL_CHUNK == 256
