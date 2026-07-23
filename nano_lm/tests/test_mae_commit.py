"""
Contract: MAE commits the block whose lookahead fitness is argmax (not block logprob).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scorers import pick_argmax


def test_given_mae_lookahead_scores_when_commit_then_argmax_fitness():
    # Candidate 0 has better immediate block logprob but worse lookahead fitness.
    block_mean = [-0.2, -1.0, -0.5]
    lookahead_fit = [-2.5, -0.4, -1.1]
    committed = pick_argmax(lookahead_fit)
    assert committed == 1
    assert committed != pick_argmax(block_mean)
