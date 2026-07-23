"""H-ENT helpers: agreement reward and head-collapse metric."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def agreement_loss(logits_a: torch.Tensor, logits_b: torch.Tensor) -> torch.Tensor:
    """
    GIVEN dual-head logits [B,T,V]
    WHEN computing agreement
    THEN return symmetric KL between softmax distributions (shifted next-token).
    """
    a = logits_a[:, :-1, :].float()
    b = logits_b[:, :-1, :].float()
    pa = F.log_softmax(a, dim=-1)
    pb = F.log_softmax(b, dim=-1)
    qa = F.softmax(a, dim=-1)
    qb = F.softmax(b, dim=-1)
    return 0.5 * (
        F.kl_div(pa, qb, reduction="batchmean")
        + F.kl_div(pb, qa, reduction="batchmean")
    )


def head_tv_distance(logits_a: torch.Tensor, logits_b: torch.Tensor) -> float:
    """
    GIVEN dual-head logits
    WHEN measuring separation
    THEN return mean total-variation distance between softmax rows (shifted).
    """
    with torch.no_grad():
        a = F.softmax(logits_a[:, :-1, :].float(), dim=-1)
        b = F.softmax(logits_b[:, :-1, :].float(), dim=-1)
        tv = 0.5 * (a - b).abs().sum(dim=-1).mean()
    return float(tv.item())


def heads_collapsed(tv: float, *, floor: float = 0.02) -> bool:
    """
    GIVEN mean TV between heads
    WHEN checking collapse
    THEN True if TV <= floor (effectively one head).
    """
    return tv <= floor
