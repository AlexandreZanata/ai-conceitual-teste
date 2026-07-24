"""
Contract: H-POOL2 warm-start + decide vs H-POOL.
"""

from __future__ import annotations

import random

from pool2_ops import (
    POOL2_GENS,
    POOL2_POP,
    decide_hpool2,
    warm_start_pop2,
)


def test_given_pool_when_warm2_then_size_and_clamped():
    rng = random.Random(0)
    pool = [
        {
            "n": 2,
            "temperature": 0.8,
            "top_p": 0.9,
            "use_mae": False,
            "k": 2,
            "block": 2,
            "horizon": 2,
        }
    ]
    out = warm_start_pop2(pool, POOL2_POP, rng)
    assert len(out) == POOL2_POP
    assert POOL2_GENS == 1


def test_given_quality_and_fwd_save_when_decide_then_promote():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 44.0, "teacher_forwards": 8.0}}
    s = {"mean_lp": -15.48, "mean_wall": 40.0, "teacher_forwards": 2.0}
    assert decide_hpool2(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 44.0, "teacher_forwards": 8.0}}
    s = {"mean_lp": -15.7, "mean_wall": 30.0, "teacher_forwards": 2.0}
    assert "quality drop" in decide_hpool2(s, stats)


def test_given_no_fwd_save_when_decide_then_kill():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 44.0, "teacher_forwards": 4.0}}
    s = {"mean_lp": -15.4, "mean_wall": 40.0, "teacher_forwards": 4.0}
    assert "no wall save" in decide_hpool2(s, stats)
