"""
Contract: magnitude prune zeros Linear weights; dual gate vs H-STAG.
"""

from __future__ import annotations

from prun_mask import density_of, magnitude_prune, sparsity_of
from prun_ops import decide_hprun, scale_flops_by_density
from student_model import build_student


def test_given_model_when_prune_then_sparsity_near_target():
    m = build_student()
    magnitude_prune(m, sparsity=0.3)
    sp = sparsity_of(m)
    assert 0.25 <= sp <= 0.35
    assert abs(density_of(m) - (1.0 - sp)) < 1e-9


def test_given_half_density_when_scale_then_half_flops():
    assert scale_flops_by_density(100.0, density=0.5) == 50.0


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 12.0}
    stats = {"H-STAG": tip}
    assert decide_hprun({"mean_lp": -16.0, "mean_gflops": 10.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_hprun({"mean_lp": -16.2, "mean_gflops": 8.0}, stats)
    assert "FLOP" in decide_hprun({"mean_lp": -15.9, "mean_gflops": 12.5}, stats)
