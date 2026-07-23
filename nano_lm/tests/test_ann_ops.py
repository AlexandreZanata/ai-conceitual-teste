"""
Contract: H-ANN promotes only when teacher_lp > KD-cos.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ann_ops import decide_hann


def test_given_anneal_better_when_decide_then_promote():
    stats = {"KD-cos": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.9, "mean_wall": 40.0}
    assert decide_hann(s, stats).startswith("PROMOTE")


def test_given_cosine_better_when_decide_then_kill():
    stats = {"KD-cos": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.6, "mean_wall": 40.0}
    assert "cosine wins" in decide_hann(s, stats)


def test_given_missing_control_when_decide_then_needs():
    assert decide_hann({"mean_lp": -16.0}, {}) == "needs KD-cos control"
