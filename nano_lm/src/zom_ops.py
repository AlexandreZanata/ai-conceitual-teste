"""Zombie helpers for H-ZOM: reinject dead weights with sign-flipped noise."""

from __future__ import annotations

from typing import Sequence

import torch


def zombie_state(
    state: dict[str, torch.Tensor], scale: float
) -> dict[str, torch.Tensor]:
    """
    GIVEN a dead individual's state_dict and noise scale
    WHEN creating a zombie
    THEN floating tensors become −v + scale·N(0,1); non-floats are cloned.
    """
    out: dict[str, torch.Tensor] = {}
    for k, v in state.items():
        if v.dtype.is_floating_point:
            out[k] = -v + scale * torch.randn_like(v)
        else:
            out[k] = v.clone()
    return out


def dead_indices(fits: Sequence[float]) -> list[int]:
    """
    GIVEN fitness scores
    WHEN marking the dead (non-breeding) half
    THEN return the worst max(1, n//2) indices (ties: higher index worse).
    """
    n = len(fits)
    if n < 1:
        raise ValueError("dead_indices: empty")
    k = max(1, n // 2)
    worst_first = sorted(range(n), key=lambda i: (fits[i], -i))
    return worst_first[:k]


def state_diverged(state: dict[str, torch.Tensor]) -> bool:
    """True if any floating tensor has NaN or Inf."""
    for v in state.values():
        if not v.dtype.is_floating_point:
            continue
        if bool(torch.isnan(v).any().item()) or bool(torch.isinf(v).any().item()):
            return True
    return False
