"""
Contract: H-TIE shares transformer blocks; dual gate vs H-STAG.
"""

from __future__ import annotations

from student_model import build_student, count_params
from tie_ops import decide_htie
from tie_student import build_tie_student, share_transformer_blocks


def test_given_student_when_share_then_fewer_unique_params():
    base = build_student()
    tied = share_transformer_blocks(build_student())
    assert count_params(tied) < count_params(base)
    assert id(tied.transformer.h[0]) == id(tied.transformer.h[1])


def test_given_build_tie_when_forward_then_shared_blocks():
    m = build_tie_student()
    assert id(m.transformer.h[0]) == id(m.transformer.h[1])


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_params": 3_300_000.0, "mean_gflops": 10.0}
    stats = {"H-STAG": tip}
    assert decide_htie(
        {"mean_lp": -16.0, "mean_params": 3_200_000.0, "mean_gflops": 10.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_htie(
        {"mean_lp": -16.2, "mean_params": 3_000_000.0, "mean_gflops": 8.0}, stats
    )
    assert "param/FLOP" in decide_htie(
        {"mean_lp": -15.9, "mean_params": 3_400_000.0, "mean_gflops": 10.5}, stats
    )
