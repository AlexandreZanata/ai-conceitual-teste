"""
Contract: H-CAP hard caps + decide vs H-POOL.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cap_ops import CAP_MAX_N, CAP_NEWS, apply_hard_caps, decide_hcap


def test_given_raw_when_apply_caps_then_on_codebooks():
    g, mn = apply_hard_caps(
        {
            "temperature": 0.8,
            "top_p": 0.9,
            "n": 5,
            "k": 1,
            "block": 1,
            "horizon": 2,
            "use_mae": False,
        },
        99,
    )
    assert g["n"] <= CAP_MAX_N
    assert mn in CAP_NEWS


def test_given_faster_quality_when_decide_then_promote():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 50.0}}
    s = {"mean_lp": -15.4, "mean_wall": 40.0}
    assert decide_hcap(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 50.0}}
    s = {"mean_lp": -15.7, "mean_wall": 30.0}
    assert "quality < POOL" in decide_hcap(s, stats)


def test_given_no_wall_when_decide_then_kill():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 40.0}}
    s = {"mean_lp": -15.4, "mean_wall": 45.0}
    assert "no wall save" in decide_hcap(s, stats)
