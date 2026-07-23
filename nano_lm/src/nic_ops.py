"""Fitness-sharing helpers for H-NIC."""

from __future__ import annotations

from typing import Any, Sequence

import torch


def flatten_floats(state: dict[str, Any]) -> torch.Tensor:
    """Concatenate float tensors from a state_dict into one CPU vector."""
    parts = [
        v.detach().float().reshape(-1).cpu()
        for v in state.values()
        if v.dtype.is_floating_point
    ]
    if not parts:
        raise ValueError("flatten_floats: no float tensors")
    return torch.cat(parts)


def mean_l2_to_others(vecs: Sequence[torch.Tensor], index: int) -> float:
    """Mean L2 from vecs[index] to all other vectors."""
    if len(vecs) < 2:
        return 0.0
    if index < 0 or index >= len(vecs):
        raise ValueError("mean_l2_to_others: index out of range")
    total = 0.0
    n = 0
    for j, v in enumerate(vecs):
        if j == index:
            continue
        total += float(torch.norm(vecs[index] - v).item())
        n += 1
    return total / max(n, 1)


def mean_crowding(vecs: Sequence[torch.Tensor], index: int) -> float:
    """
    GIVEN flattened weight vectors and an index
    WHEN measuring niche crowding
    THEN return mean_j 1/(1+L2(i,j)) — high when neighbors are close.
    """
    if len(vecs) < 2:
        return 0.0
    if index < 0 or index >= len(vecs):
        raise ValueError("mean_crowding: index out of range")
    total = 0.0
    n = 0
    for j in range(len(vecs)):
        if j == index:
            continue
        d = float(torch.norm(vecs[index] - vecs[j]).item())
        total += 1.0 / (1.0 + d)
        n += 1
    return total / max(n, 1)


def share_fitness(
    raw_fits: Sequence[float],
    states: Sequence[dict[str, Any]],
    alpha: float,
) -> list[float]:
    """
    GIVEN raw fitness and state_dicts
    WHEN applying fitness sharing
    THEN shared[i] = raw[i] − α · mean_j 1/(1+L2(i,j))
    (penalizes weight-space crowding).
    """
    if len(raw_fits) != len(states):
        raise ValueError("share_fitness: length mismatch")
    if alpha < 0:
        raise ValueError("share_fitness: alpha must be >= 0")
    vecs = [flatten_floats(st) for st in states]
    return [
        float(raw_fits[i]) - alpha * mean_crowding(vecs, i)
        for i in range(len(raw_fits))
    ]
