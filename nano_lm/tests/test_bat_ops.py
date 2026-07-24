"""Contract: H-BAT left-pad + throughput dual gate vs serial EARLY."""

from __future__ import annotations

from bat_ops import decide_hbat, left_pad_batch


def test_given_seqs_when_left_pad_then_aligned() -> None:
    ids, masks, lens = left_pad_batch([[1, 2, 3], [4]], pad_id=0)
    assert ids == [[1, 2, 3], [0, 0, 4]]
    assert masks == [[1, 1, 1], [0, 0, 1]]
    assert lens == [3, 1]


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_tps": 100.0}
    stats = {"H-EARLY": tip}
    assert decide_hbat(
        {"mean_lp": -16.02, "mean_tps": 150.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hbat(
        {"mean_lp": -16.2, "mean_tps": 200.0}, stats
    )
    assert "tok/s" in decide_hbat(
        {"mean_lp": -16.0, "mean_tps": 90.0}, stats
    )
