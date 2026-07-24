"""Contract: H-BUCKET length bands + dual gate vs H-BAT."""

from __future__ import annotations

from bucket_ops import assign_length_buckets, decide_hbucket


def test_given_lengths_when_assign_then_band_groups() -> None:
    groups = assign_length_buckets([9, 12, 13, 16], band=4)
    assert groups == [[0, 1], [2, 3]]


def test_given_same_band_when_assign_then_single_bucket() -> None:
    assert assign_length_buckets([10, 11, 12], band=4) == [[0, 1, 2]]


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    bat = {"mean_lp": -16.0, "mean_tps": 200.0}
    early = {"mean_lp": -16.0, "mean_tps": 100.0}
    stats = {"H-BAT": bat, "H-EARLY": early}
    assert decide_hbucket(
        {"mean_lp": -16.02, "mean_tps": 250.0}, stats
    ).startswith("PROMOTE")
    assert "lp change vs H-BAT" in decide_hbucket(
        {"mean_lp": -16.2, "mean_tps": 300.0}, stats
    )
    assert "serial EARLY" in decide_hbucket(
        {"mean_lp": -16.0, "mean_tps": 250.0},
        {"H-BAT": bat, "H-EARLY": {"mean_lp": -16.2, "mean_tps": 100.0}},
    )
    assert "tok/s" in decide_hbucket(
        {"mean_lp": -16.0, "mean_tps": 180.0}, stats
    )
