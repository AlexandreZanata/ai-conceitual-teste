"""H-ADV: weak discriminator helpers; decide vs B2 on collapse/quality."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn as nn
import torch.nn.functional as F

__all__ = [
    "WeakDisc",
    "soft_topk_feats",
    "disc_bce",
    "pred_entropy",
    "mode_collapsed",
    "decide_hadv",
]

TOP_K = 32


class WeakDisc(nn.Module):
    """Linear real/fake head on pooled top-k soft features."""

    def __init__(self, k: int = TOP_K) -> None:
        super().__init__()
        self.fc = nn.Linear(int(k), 1)

    def forward(self, feats: torch.Tensor) -> torch.Tensor:
        return self.fc(feats).squeeze(-1)


def soft_topk_feats(logits: torch.Tensor, *, k: int = TOP_K) -> torch.Tensor:
    """
    GIVEN next-token logits [B,T,V]
    WHEN pooling shifted softmax top-k masses
    THEN return [B,k] features for the discriminator.
    """
    if k < 1:
        raise ValueError("soft_topk_feats: k must be >= 1")
    probs = F.softmax(logits[:, :-1, :].float(), dim=-1)
    vals, _ = probs.topk(min(int(k), probs.shape[-1]), dim=-1)
    return vals.mean(dim=1)


def disc_bce(logits: torch.Tensor, *, real: bool) -> torch.Tensor:
    """BCE-with-logits for real=1 / fake=0 targets."""
    target = torch.ones_like(logits) if real else torch.zeros_like(logits)
    return F.binary_cross_entropy_with_logits(logits, target)


def pred_entropy(logits: torch.Tensor) -> float:
    """Mean predictive entropy over shifted positions."""
    p = F.softmax(logits[:, :-1, :].float(), dim=-1)
    h = -(p * (p.clamp_min(1e-12).log())).sum(dim=-1).mean()
    return float(h.item())


def mode_collapsed(
    h0: float, h1: float, *, min_ratio: float = 0.25, floor: float = 1e-6
) -> bool:
    """
    GIVEN initial and final predictive entropy
    WHEN checking GAN mode collapse
    THEN True if final <= floor or final/initial < min_ratio.
    """
    if float(h1) <= floor:
        return True
    if float(h0) <= floor:
        return float(h1) <= floor
    return (float(h1) / float(h0)) < float(min_ratio)


def decide_hadv(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ADV vs B2
    WHEN deciding
    THEN KILL on mode collapse or ≤ B2; else PROMOTE.
    """
    if float(s.get("mode_collapsed", 0.0)) > 0.0 or float(s.get("collapsed", 0.0)) > 0.0:
        return "KILL (mode collapse)"
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
