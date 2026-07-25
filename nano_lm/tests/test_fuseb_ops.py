"""Contract: H-FUSEB dual gate vs H-CHBAT + FUSEB_CHUNK constant."""

from __future__ import annotations

from chbat_ops import CHBAT_CHUNK
from fuseb_ops import FUSEB_CHUNK, decide_hfuseb
from kvsel_ops import should_use_kv


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    # GIVEN H-CHBAT control WHEN FUSEB wins tok/s or wall within ε THEN PROMOTE
    tip = {"mean_lp": -16.0, "mean_tps": 100.0, "mean_wall": 40.0}
    stats = {"H-CHBAT": tip}
    assert decide_hfuseb(
        {"mean_lp": -16.02, "mean_tps": 150.0, "mean_wall": 40.0}, stats
    ).startswith("PROMOTE")
    assert decide_hfuseb(
        {"mean_lp": -16.0, "mean_tps": 100.0, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hfuseb(
        {"mean_lp": -16.2, "mean_tps": 200.0, "mean_wall": 10.0}, stats
    )
    assert "tok/s/wall" in decide_hfuseb(
        {"mean_lp": -16.0, "mean_tps": 90.0, "mean_wall": 50.0}, stats
    )
    assert decide_hfuseb(
        {"mean_lp": -16.0, "mean_tps": 150.0, "mean_wall": 10.0}, {}
    ).startswith("needs H-CHBAT")


def test_given_fuseb_chunk_when_gate_then_matches_chbat_and_kvsel() -> None:
    assert FUSEB_CHUNK == CHBAT_CHUNK == 256
    assert should_use_kv(64, 48) is True
    assert should_use_kv(16, 48) is False
