"""
Contract: H-SYS free-lunch gate vs CURL default + tip@B2.
"""

from __future__ import annotations

from sys_ops import SYS_SEQ_LO, SYS_STAGES, decide_hsys, decide_hsys_arm


def test_given_tip_knobs_when_import_then_curl_official():
    assert SYS_SEQ_LO == 8
    assert SYS_STAGES == 3


def test_given_arm_beats_both_when_decide_then_promote():
    stats = {
        "H-CURL": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-EARLY": {"mean_lp": -16.8, "mean_wall": 45.0},
    }
    assert decide_hsys_arm(
        {"mean_lp": -16.5, "mean_wall": 40.0}, stats, tip_family="H-EARLY"
    ).startswith("PROMOTE")


def test_given_free_lunch_when_decide_then_kill():
    stats = {
        "H-CURL": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 45.0},
        "H-POOL": {"mean_lp": -16.4, "mean_wall": 48.0},
        "H-SYS-E": {"mean_lp": -16.9, "mean_wall": 40.0},
        "H-SYS-P": {"mean_lp": -16.45, "mean_wall": 47.0},
    }
    assert "≤ H-EARLY@B2" in decide_hsys_arm(
        stats["H-SYS-E"], stats, tip_family="H-EARLY"
    )
    assert decide_hsys(stats).startswith("KILL")


def test_given_any_arm_wins_when_decide_then_promote():
    stats = {
        "H-CURL": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-EARLY": {"mean_lp": -16.8, "mean_wall": 45.0},
        "H-POOL": {"mean_lp": -16.7, "mean_wall": 48.0},
        "H-SYS-E": {"mean_lp": -16.9, "mean_wall": 40.0},
        "H-SYS-P": {"mean_lp": -16.5, "mean_wall": 47.0},
    }
    assert decide_hsys(stats).startswith("PROMOTE")
