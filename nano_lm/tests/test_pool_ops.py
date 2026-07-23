"""
Contract: warm-start fills from pool; H-POOL must beat cold H-DECKL.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pool_ops import decide_hpool, warm_start_pop


def _gene(n: int = 2) -> dict:
    return {
        "temperature": 0.8,
        "top_p": 0.9,
        "n": n,
        "k": 2,
        "block": 1,
        "horizon": 2,
        "use_mae": False,
    }


def test_given_pool_when_warm_start_then_size_and_pool_prefix():
    rng = random.Random(0)
    pool = [_gene(1), _gene(3)]
    pop = warm_start_pop(pool, 4, rng)
    assert len(pop) == 4
    assert pop[0]["n"] == 1
    assert pop[1]["n"] == 3


def test_given_empty_pool_when_warm_start_then_raises():
    try:
        warm_start_pop([], 2, random.Random(0))
        assert False, "expected ValueError"
    except ValueError as e:
        assert "empty pool" in str(e)


def test_given_better_lp_when_decide_then_promote():
    stats = {"H-DECKL": {"mean_lp": -16.0}}
    s = {"mean_lp": -15.5}
    assert decide_hpool(s, stats).startswith("PROMOTE")


def test_given_worse_lp_when_decide_then_kill():
    stats = {"H-DECKL": {"mean_lp": -16.0}}
    s = {"mean_lp": -16.5}
    assert "≤ cold H-DECKL" in decide_hpool(s, stats)
