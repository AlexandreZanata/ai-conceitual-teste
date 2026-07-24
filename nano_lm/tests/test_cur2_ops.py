"""
Contract: H-CUR2 promotes only when some n_stages beats H-CUR (n=3).
"""

from __future__ import annotations

from cur2_ops import best_n_stages, decide_hcur2, mean_lp_by_stages


def test_given_rows_when_mean_by_n_then_averages():
    rows = [
        {"n_stages": 2, "teacher_mean_logprob": -10.0},
        {"n_stages": 2, "teacher_mean_logprob": -12.0},
        {"n_stages": 3, "teacher_mean_logprob": -11.0},
    ]
    assert mean_lp_by_stages(rows) == {2: -11.0, 3: -11.0}


def test_given_n4_better_when_decide_then_promote():
    lp = {2: -17.0, 3: -16.5, 4: -16.0, 5: -16.2}
    assert decide_hcur2(lp).startswith("PROMOTE")
    assert best_n_stages(lp) == 4


def test_given_n3_best_when_decide_then_kill():
    lp = {2: -17.0, 3: -16.0, 4: -16.5, 5: -16.2}
    assert "best n ≤ H-CUR" in decide_hcur2(lp)
