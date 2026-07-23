"""
Contract: formal means + decide vs B2 (promote only if hyp > B2, no overfit).
GIVEN formal rows for H-HOLD and B2
WHEN decide_formal_vs_b2 runs
THEN PROMOTE confirmed iff H-HOLD lp > B2 and overfit flag clear.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from formal_ops import decide_formal_vs_b2, means_by_family


def test_given_rows_when_means_then_family_lp():
    rows = [
        {"family": "B2", "teacher_mean_logprob": -14.0, "mean_wall_ms": 100},
        {"family": "B2", "teacher_mean_logprob": -16.0, "mean_wall_ms": 120},
        {"family": "H-HOLD", "teacher_mean_logprob": -15.0, "mean_wall_ms": 80},
    ]
    s = means_by_family(rows)
    assert s["B2"]["lp"] == -15.0
    assert s["H-HOLD"]["n"] == 1.0


def test_given_better_when_formal_then_promote():
    stats = {
        "B2": {"lp": -15.0, "wall": 100.0, "n": 3.0, "overfit": 0.0},
        "H-HOLD": {"lp": -14.5, "wall": 90.0, "n": 3.0, "overfit": 0.0},
    }
    assert decide_formal_vs_b2("H-HOLD", stats) == (
        "PROMOTE confirmed (H-HOLD > B2)"
    )


def test_given_worse_when_formal_then_reverse():
    stats = {
        "B2": {"lp": -14.0, "wall": 100.0, "n": 3.0, "overfit": 0.0},
        "H-HOLD": {"lp": -16.0, "wall": 90.0, "n": 3.0, "overfit": 0.0},
    }
    assert decide_formal_vs_b2("H-HOLD", stats) == (
        "KILL / reverse smoke (H-HOLD ≤ B2)"
    )


def test_given_overfit_when_formal_then_kill():
    stats = {
        "B2": {"lp": -15.0, "wall": 100.0, "n": 3.0, "overfit": 0.0},
        "H-HOLD": {"lp": -14.0, "wall": 90.0, "n": 3.0, "overfit": 1.0},
    }
    assert decide_formal_vs_b2("H-HOLD", stats) == "KILL (overfit; H-HOLD)"
