"""
Contract: H-CASC needs forward save vs full H-DEC and must beat B4.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from casc_ops import cascade_forward_budget, decide_hcasc, wall_saved


def test_given_cascade_when_budget_then_less_than_full():
    casc, full = cascade_forward_budget(
        pop_size=4, generations=2, n_prompts=2, mid_k=2, final_k=1
    )
    assert casc == 12  # 2 gens * (2+1) * 2
    assert full == 16
    assert wall_saved(casc, full) is True


def test_given_better_and_save_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "wall_save": 1.0}
    assert decide_hcasc(s, stats).startswith("PROMOTE")


def test_given_no_save_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0}}
    s = {"mean_lp": -15.0, "wall_save": 0.0}
    assert "no teacher-forward save" in decide_hcasc(s, stats)


def test_given_worse_than_b4_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -16.0}}
    s = {"mean_lp": -16.5, "wall_save": 1.0}
    assert "≤ B4" in decide_hcasc(s, stats)
