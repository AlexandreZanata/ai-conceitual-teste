"""Contract: H-CHB pick best B + dual gate vs H-CHUNK tip."""

from __future__ import annotations

from chb_ops import decide_hchb, pick_chb_size


def test_given_scored_when_pick_then_quality_ok_min_wall() -> None:
    # GIVEN per-B scores / WHEN pick / THEN quality-ok with min wall
    scored = {
        32: {"mean_lp": -16.0, "mean_wall": 50.0},
        64: {"mean_lp": -16.0, "mean_wall": 40.0},
        128: {"mean_lp": -16.2, "mean_wall": 30.0},  # quality fail
    }
    assert pick_chb_size(scored, early_lp=-16.0) == 64


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_wall": 200.0},
        "H-CHUNK": {"mean_lp": -16.0, "mean_wall": 50.0},
    }
    assert decide_hchb(
        {"mean_lp": -16.0, "mean_wall": 40.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hchb(
        {"mean_lp": -16.2, "mean_wall": 30.0}, stats
    )
    assert "tip wall" in decide_hchb(
        {"mean_lp": -15.9, "mean_wall": 50.0}, stats
    )
    assert decide_hchb({"mean_lp": -16.0, "mean_wall": 40.0}, {}).startswith(
        "needs H-EARLY"
    )
