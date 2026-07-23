"""H-HEB: local Hebbian weight update helpers; decide vs B2."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

import torch

__all__ = ["hebbian_delta", "apply_hebbian", "diverged", "decide_hheb"]

LOSS_RATIO = 10.0


def hebbian_delta(
    pre: torch.Tensor, post: torch.Tensor, *, eta: float
) -> torch.Tensor:
    """
    GIVEN pre [..., in] and post [..., out]
    WHEN forming a Hebbian delta for Linear weight [out, in]
    THEN return η · mean(postᵀ pre) over leading dims.
    """
    if eta < 0.0:
        raise ValueError("hebbian_delta: eta must be >= 0")
    x = pre.reshape(-1, pre.shape[-1]).float()
    y = post.reshape(-1, post.shape[-1]).float()
    if x.shape[0] != y.shape[0]:
        raise ValueError("hebbian_delta: batch mismatch")
    n = max(1, int(x.shape[0]))
    return (eta / n) * (y.transpose(0, 1) @ x)


def apply_hebbian(
    weight: torch.Tensor, pre: torch.Tensor, post: torch.Tensor, *, eta: float
) -> None:
    """In-place weight += Hebbian delta (no grad)."""
    with torch.no_grad():
        weight.add_(hebbian_delta(pre, post, eta=eta).to(dtype=weight.dtype))


def diverged(losses: Sequence[float]) -> bool:
    """
    GIVEN a loss history
    WHEN checking stability
    THEN true if any non-finite or last > LOSS_RATIO × first finite.
    """
    finite = [float(x) for x in losses if math.isfinite(float(x))]
    if len(finite) != len(losses) or not finite:
        return True
    return finite[-1] > LOSS_RATIO * max(finite[0], 1e-8)


def decide_hheb(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-HEB vs B2
    WHEN deciding
    THEN KILL if diverged or ≤ B2; else PROMOTE.
    """
    if float(s.get("diverged", 0.0)) > 0.0 or float(s.get("unstable", 0.0)) > 0.0:
        return "KILL (diverged)"
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
