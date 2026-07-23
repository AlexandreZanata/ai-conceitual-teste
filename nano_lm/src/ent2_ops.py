"""H-ENT2 helpers: TV floor penalty (anti-collapse) + decision vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

TV_TAU = 0.02


def tv_floor_loss(
    logits_a: torch.Tensor, logits_b: torch.Tensor, *, tau: float
) -> torch.Tensor:
    """
    GIVEN dual-head logits and tau > 0
    WHEN mean TV between softmax heads is below tau
    THEN return relu(tau − TV) (differentiable floor penalty).
    """
    if tau <= 0.0:
        raise ValueError("tv_floor_loss: tau must be > 0")
    a = F.softmax(logits_a[:, :-1, :].float(), dim=-1)
    b = F.softmax(logits_b[:, :-1, :].float(), dim=-1)
    tv = 0.5 * (a - b).abs().sum(dim=-1).mean()
    return F.relu(torch.as_tensor(tau, device=tv.device, dtype=tv.dtype) - tv)


def decide_hent2(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ENT2 family stats
    WHEN deciding
    THEN KILL if collapsed again; else require beat B2 with distinct heads.
    """
    if float(s.get("collapsed", 0.0)) > 0.0:
        return "KILL (collapsed again)"
    b2 = stats.get("B2", {}).get("mean_lp")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2) + 1e-6:
        return "PROMOTE (beats B2, heads distinct)"
    return "KILL / hold (≤ B2)"
