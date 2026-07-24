"""
Contract: H-FLOP tokens/s + est FLOPs + instrumentation decide.
"""

from __future__ import annotations

from flop_ops import decide_hflop, est_decode_flops, to_gflops, tokens_per_s


def test_given_tokens_when_tps_then_scale():
    assert abs(tokens_per_s(n_new=10, wall_ms=1000.0) - 10.0) < 1e-9
    assert tokens_per_s(n_new=0, wall_ms=10.0) == 0.0


def test_given_ar_when_flops_then_exact_sum():
    # n=2, p=3, t=2 → steps = 2*3 + 2*3/2 = 6+3 = 9; flops = 2*2*9 = 36
    assert est_decode_flops(n_params=2, prompt_len=3, n_new=2) == 36.0


def test_given_beam_evals_when_flops_then_avg_len():
    # token_evals=4, p=2, t=2 → avg=3; 2*10*4*3 = 240
    got = est_decode_flops(n_params=10, prompt_len=2, n_new=2, token_evals=4)
    assert got == 240.0


def test_given_metrics_when_decide_then_promote():
    stats = {
        "B3": {"mean_tps": 100.0, "mean_gflops": 1.2},
        "H-EARLY": {"mean_tps": 120.0, "mean_gflops": 0.9},
    }
    assert decide_hflop(stats).startswith("PROMOTE")


def test_given_missing_when_decide_then_kill():
    assert "KILL" in decide_hflop({"B3": {"mean_tps": 1.0}})
    assert to_gflops(1e9) == 1.0
