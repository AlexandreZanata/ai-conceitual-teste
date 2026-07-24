"""Contract: H-MIX protocol gate vs PRUN (never tip PROMOTE)."""

from __future__ import annotations

from mix_ops import decide_hmix


def test_given_mix_when_decide_then_protocol_or_kill() -> None:
    # GIVEN PRUN control WHEN mix beats wall with quality THEN PROTOCOL
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-PRUN": tip}
    out = decide_hmix({"mean_lp": -16.0, "mean_wall": 60.0}, stats)
    assert out.startswith("PROTOCOL")
    assert "tip" in out
    assert "PROMOTE" not in out


def test_given_quality_drop_when_decide_then_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-PRUN": tip}
    assert "quality" in decide_hmix(
        {"mean_lp": -16.2, "mean_wall": 50.0}, stats
    )


def test_given_no_wall_win_when_decide_then_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-PRUN": tip}
    assert "wall" in decide_hmix(
        {"mean_lp": -15.9, "mean_wall": 70.0}, stats
    )
