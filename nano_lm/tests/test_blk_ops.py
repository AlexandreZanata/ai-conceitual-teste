"""
Contract: H-BLK block-parallel decision vs B3; decode emits block chunks.
"""

from __future__ import annotations

from blk_ops import decide_hblk
from decode_block import decode_block


def test_given_crash_when_decide_then_kill_crash():
    stats = {"B3": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hblk({"mean_lp": -17.7, "mean_wall": 40.0}, stats) == (
        "KILL (quality crash)"
    )


def test_given_drop_when_decide_then_kill_drop():
    stats = {"B3": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hblk({"mean_lp": -17.2, "mean_wall": 40.0}, stats) == (
        "KILL (quality drop vs B3)"
    )


def test_given_no_speedup_when_decide_then_kill():
    stats = {"B3": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hblk({"mean_lp": -16.9, "mean_wall": 90.0}, stats) == (
        "KILL (no speedup vs B3)"
    )


def test_given_dual_win_when_decide_then_promote():
    stats = {"B3": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hblk({"mean_lp": -16.9, "mean_wall": 40.0}, stats).startswith(
        "PROMOTE"
    )


def test_given_missing_b3_when_decide_then_needs_control():
    assert decide_hblk({"mean_lp": -16.0}, {}) == "needs B3 control"


def test_given_bad_block_when_decode_then_raises():
    class _Tok:
        eos_token_id = 0

        def encode(self, *_a, **_k):
            import torch

            return torch.tensor([[1, 2]])

        def decode(self, *_a, **_k):
            return ""

    try:
        decode_block(
            None,
            _Tok(),
            "x",
            max_new_tokens=4,
            block_size=0,
            temperature=1.0,
            top_p=1.0,
            seed=0,
            device=__import__("torch").device("cpu"),
        )
        assert False, "expected ValueError"
    except ValueError as e:
        assert "block_size" in str(e)
