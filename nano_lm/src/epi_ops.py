"""H-EPI: context-dependent LR scale + embed mask; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

__all__ = [
    "mean_token_entropy",
    "context_lr_scale",
    "should_mask_embeds",
    "zero_embed_grads",
    "decide_hepi",
]


def mean_token_entropy(logits: torch.Tensor) -> float:
    """
    GIVEN logits [B, T, V]
    WHEN measuring teacher context difficulty
    THEN return mean token entropy (nats).
    """
    p = F.softmax(logits.float(), dim=-1)
    ent = -(p * (p + 1e-12).log()).sum(dim=-1)
    return float(ent.mean().item())


def context_lr_scale(
    entropy: float,
    *,
    ent_lo: float,
    ent_hi: float,
    scale_lo: float = 0.5,
    scale_hi: float = 1.5,
) -> float:
    """
    GIVEN batch entropy and bounds
    WHEN mapping to an LR multiplier
    THEN linear map entropy∈[lo,hi] → [scale_lo, scale_hi] (clamped).
    """
    if ent_hi <= ent_lo:
        raise ValueError("context_lr_scale: ent_hi must be > ent_lo")
    if scale_hi < scale_lo:
        raise ValueError("context_lr_scale: scale_hi must be >= scale_lo")
    t = (float(entropy) - float(ent_lo)) / (float(ent_hi) - float(ent_lo))
    t = min(1.0, max(0.0, t))
    return float(scale_lo + (scale_hi - scale_lo) * t)


def should_mask_embeds(entropy: float, *, threshold: float) -> bool:
    """
    GIVEN batch entropy and threshold
    WHEN deciding embed plasticity
    THEN mask embeds iff entropy < threshold (easy context).
    """
    return float(entropy) < float(threshold)


def zero_embed_grads(student: object) -> None:
    """Zero wte grads when present (context mask)."""
    wte = getattr(getattr(student, "transformer", None), "wte", None)
    if wte is None:
        return
    for p in wte.parameters():
        if p.grad is not None:
            p.grad.zero_()


def decide_hepi(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-EPI vs B2 (fixed LR)
    WHEN deciding
    THEN PROMOTE only if teacher_lp > B2; else KILL.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats fixed LR / B2)"
    return "KILL (≤ fixed LR / B2)"
