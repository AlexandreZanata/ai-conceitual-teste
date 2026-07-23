"""
Contract: BoN selects the candidate with max mean_logprob (shared pick_argmax).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scorers import DecodeResult, pick_argmax


def _fake(mean_lp: float) -> DecodeResult:
    return DecodeResult(
        token_ids=(1, 2),
        text="x",
        mean_logprob=mean_lp,
        wall_ms=1.0,
        token_evals=2,
    )


def test_given_bon_candidates_when_select_then_max_mean_logprob_wins():
    cands = [_fake(-2.0), _fake(-0.1), _fake(-1.5)]
    idx = pick_argmax([c.mean_logprob for c in cands])
    assert idx == 1
    assert cands[idx].mean_logprob == pytest.approx(-0.1)
