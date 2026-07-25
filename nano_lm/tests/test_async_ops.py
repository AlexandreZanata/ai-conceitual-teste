"""Contract: H-ASYNC e2e gate vs H-PIN + single-batch top-k build."""

from __future__ import annotations

import torch

from async_cache import build_one_topk
from async_ops import decide_hasync, e2e_wall_s


class _Teacher:
    def __init__(self) -> None:
        self.device = torch.device("cpu")
        self.model = _M()


class _M(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(32, 8)

    def forward(self, ids: torch.Tensor):
        # logits [B,T,V]
        x = self.emb(ids.clamp(0, 31))
        logits = x @ self.emb.weight.T
        return type("O", (), {"logits": logits})()


def test_given_seq_when_e2e_then_sum() -> None:
    assert e2e_wall_s(cache_build_s=1.5, train_wall_s=2.5) == 4.0


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_e2e_wall": 1.0}
    stats = {"H-PIN": tip}
    assert decide_hasync(
        {"mean_lp": -16.0, "mean_e2e_wall": 0.8}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hasync(
        {"mean_lp": -16.2, "mean_e2e_wall": 0.5}, stats
    )
    assert "end-to-end" in decide_hasync(
        {"mean_lp": -15.9, "mean_e2e_wall": 1.0}, stats
    )
    assert decide_hasync(
        {"mean_lp": -16.0, "mean_e2e_wall": 0.8}, {}
    ).startswith("needs H-PIN")


def test_given_batch_when_build_one_then_shapes() -> None:
    # GIVEN tiny teacher / WHEN one top-k record / THEN idx/val rank-3
    ids = torch.randint(0, 32, (2, 4), dtype=torch.long)
    rec = build_one_topk(_Teacher(), ids, top_k=3)
    assert rec["topk_idx"].shape == (2, 4, 3)
    assert rec["topk_val"].shape == (2, 4, 3)
    assert rec["topk_idx"].dtype == torch.int32
    assert rec["topk_val"].dtype == torch.float16
