"""
Contract: H-DECK2 promotes only when some top_k beats H-DECK (k=2).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from deck2_ops import best_top_k, decide_hdeck2, mean_lp_by_top_k


def test_given_rows_when_mean_by_k_then_averages():
    rows = [
        {"top_k": 1, "teacher_mean_logprob": -10.0},
        {"top_k": 1, "teacher_mean_logprob": -12.0},
        {"top_k": 2, "teacher_mean_logprob": -11.0},
    ]
    assert mean_lp_by_top_k(rows) == {1: -11.0, 2: -11.0}


def test_given_k3_better_when_decide_then_promote():
    lp = {1: -17.0, 2: -16.5, 3: -16.0}
    assert decide_hdeck2(lp).startswith("PROMOTE")
    assert best_top_k(lp) == 3


def test_given_k2_best_when_decide_then_kill():
    lp = {1: -17.0, 2: -16.0, 3: -16.5}
    assert "best k ≤ H-DECK" in decide_hdeck2(lp)
