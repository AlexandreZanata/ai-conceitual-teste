"""
Contract: H-DECK gate requires quality near H-DEC and fewer teacher forwards.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from deck_ops import decide_hdeck, teacher_forward_budget, wall_saved


def test_given_top_k_when_budget_then_strictly_less_than_full():
    lofi, full = teacher_forward_budget(
        pop_size=4, generations=2, n_prompts=2, top_k=2
    )
    assert lofi == 8
    assert full == 16
    assert wall_saved(lofi, full) is True


def test_given_quality_and_save_when_decide_then_promote():
    stats = {"H-DEC": {"mean_lp": -16.9}}
    s = {"mean_lp": -16.92, "wall_save": 1.0}
    assert decide_hdeck(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-DEC": {"mean_lp": -16.0}}
    s = {"mean_lp": -17.0, "wall_save": 1.0}
    assert "worse quality" in decide_hdeck(s, stats)
