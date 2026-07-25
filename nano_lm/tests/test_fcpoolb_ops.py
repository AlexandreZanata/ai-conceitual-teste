"""Contract: H-FCPOOLB dual gate vs H-CPOOLB + chunk constant."""

from __future__ import annotations

from cpoolb_ops import CPOOLB_CHUNK
from fcpoolb_ops import FCPOOLB_CHUNK, decide_hfcpoolb
from kvsel_ops import should_use_kv


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_tps": 100.0, "mean_wall": 40.0}
    stats = {"H-CPOOLB": tip}
    assert decide_hfcpoolb(
        {"mean_lp": -16.02, "mean_tps": 150.0, "mean_wall": 40.0}, stats
    ).startswith("PROMOTE")
    assert decide_hfcpoolb(
        {"mean_lp": -16.0, "mean_tps": 100.0, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hfcpoolb(
        {"mean_lp": -16.2, "mean_tps": 200.0, "mean_wall": 10.0}, stats
    )
    assert "tok/s/wall" in decide_hfcpoolb(
        {"mean_lp": -16.0, "mean_tps": 90.0, "mean_wall": 50.0}, stats
    )
    assert decide_hfcpoolb(
        {"mean_lp": -16.0, "mean_tps": 150.0, "mean_wall": 10.0}, {}
    ).startswith("needs H-CPOOLB")


def test_given_fcpoolb_chunk_when_gate_then_matches_cpoolb_and_kvsel() -> None:
    assert FCPOOLB_CHUNK == CPOOLB_CHUNK == 256
    assert should_use_kv(64, 48) is True
    assert should_use_kv(16, 48) is False
