"""Contract: H-LAYB dual gate vs H-FUSEB + batched LAY emits tokens."""

from __future__ import annotations

import torch

from decode_lay_batch import decode_lay_batch
from layb_ops import LAYB_CHUNK, decide_hlayb
from student_model import build_student


class _Tok:
    pad_token_id = 0
    eos_token_id = 0

    def encode(self, text: str, add_special_tokens: bool = True):
        return list(range(1, len(text.split()) + 1)) or [1]

    def decode(self, ids: list[int], skip_special_tokens: bool = True) -> str:
        return " ".join(str(i) for i in ids)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_tps": 100.0, "mean_wall": 40.0}
    stats = {"H-FUSEB": tip}
    assert decide_hlayb(
        {"mean_lp": -16.02, "mean_tps": 150.0, "mean_wall": 40.0}, stats
    ).startswith("PROMOTE")
    assert decide_hlayb(
        {"mean_lp": -16.0, "mean_tps": 100.0, "mean_wall": 30.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hlayb(
        {"mean_lp": -16.2, "mean_tps": 200.0, "mean_wall": 10.0}, stats
    )
    assert "tok/s/wall" in decide_hlayb(
        {"mean_lp": -16.0, "mean_tps": 90.0, "mean_wall": 50.0}, stats
    )
    assert decide_hlayb(
        {"mean_lp": -16.0, "mean_tps": 150.0, "mean_wall": 10.0}, {}
    ).startswith("needs H-FUSEB")


def test_given_batch_when_lay_decode_then_emits_tokens() -> None:
    assert LAYB_CHUNK == 256
    m = build_student(50257).eval()
    device = torch.device("cpu")
    tok = _Tok()
    prompts = [" ".join(["once"] * 12), " ".join(["upon"] * 8)]
    results, wall = decode_lay_batch(
        m,
        tok,
        prompts,
        n=1,
        max_new_tokens=4,
        min_new=1,
        conf_threshold=0.99,
        patience=8,
        temperature=0.0,
        top_p=1.0,
        max_skip=1,
        lay_conf=0.0,
        seed=0,
        device=device,
    )
    assert len(results) == 2
    assert all(len(r.token_ids) >= 1 for r in results)
    assert wall > 0.0
    assert all((r.layer_evals or 0) >= 1 for r in results)
