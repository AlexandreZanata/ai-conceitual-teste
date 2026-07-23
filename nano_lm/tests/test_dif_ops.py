"""
Contract: H-DIF corrupt + decide vs B2 on VRAM/slow/quality.
"""

from __future__ import annotations

import torch

from dif_ops import VRAM_STOP_MIB, corrupt_tokens, decide_hdif


def test_given_rate_when_corrupt_then_mask_applied():
    ids = torch.arange(8).reshape(2, 4)
    noisy, noise = corrupt_tokens(ids, rate=1.0, mask_id=99)
    assert bool(noise.all())
    assert int((noisy == 99).sum().item()) == 8


def test_given_zero_rate_when_corrupt_then_unchanged():
    ids = torch.arange(4).reshape(1, 4)
    noisy, noise = corrupt_tokens(ids, rate=0.0, mask_id=99)
    assert not bool(noise.any())
    assert torch.equal(noisy, ids)


def test_given_vram_when_decide_then_kill_vram():
    stats = {"B2": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.0, "mean_wall": 40.0, "peak_vram_mib": VRAM_STOP_MIB + 1}
    assert decide_hdif(s, stats) == "KILL (VRAM)"


def test_given_slow_when_decide_then_kill_slow():
    stats = {"B2": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.0, "mean_wall": 120.0, "peak_vram_mib": 100.0}
    assert decide_hdif(s, stats) == "KILL (too slow)"


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -17.1, "mean_wall": 40.0, "peak_vram_mib": 100.0}
    assert decide_hdif(s, stats) == "KILL (≤ B2)"


def test_given_beats_b2_cheap_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.5, "mean_wall": 40.0, "peak_vram_mib": 100.0}
    assert decide_hdif(s, stats).startswith("PROMOTE")
