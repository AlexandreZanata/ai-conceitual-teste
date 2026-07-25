"""Contract: H-GALLF dual gate vs H-GRAPHF."""

from __future__ import annotations

from gallf_ops import GALLF_CHUNK, decide_hgallf


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 40.0}
    stats = {"H-GRAPHF": tip}
    assert decide_hgallf(
        {"mean_lp": -16.02, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hgallf(
        {"mean_lp": -16.2, "mean_wall": 10.0}, stats
    )
    assert "wall win" in decide_hgallf(
        {"mean_lp": -16.0, "mean_wall": 50.0}, stats
    )
    assert decide_hgallf({"mean_lp": -16.0, "mean_wall": 10.0}, {}).startswith(
        "needs H-GRAPHF"
    )


def test_given_chunk_when_gallf_then_matches_graphf() -> None:
    assert GALLF_CHUNK == 256
