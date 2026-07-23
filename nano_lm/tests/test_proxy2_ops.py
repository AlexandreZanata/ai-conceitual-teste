"""
Contract: H-PROXY2 promotes only when CE proxy beats H-DECK @ ≤ forwards.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from proxy2_ops import decide_hproxy2


def test_given_better_lp_same_forwards_when_decide_then_promote():
    stats = {"H-DECK": {"mean_lp": -16.0, "teacher_forwards": 8.0}}
    s = {"mean_lp": -15.5, "teacher_forwards": 8.0}
    assert decide_hproxy2(s, stats).startswith("PROMOTE")


def test_given_worse_quality_when_decide_then_kill():
    stats = {"H-DECK": {"mean_lp": -16.0, "teacher_forwards": 8.0}}
    s = {"mean_lp": -16.5, "teacher_forwards": 8.0}
    assert "≤ H-DECK" in decide_hproxy2(s, stats)


def test_given_more_forwards_when_decide_then_kill():
    stats = {"H-DECK": {"mean_lp": -16.0, "teacher_forwards": 8.0}}
    s = {"mean_lp": -15.0, "teacher_forwards": 16.0}
    assert "more teacher forwards" in decide_hproxy2(s, stats)
