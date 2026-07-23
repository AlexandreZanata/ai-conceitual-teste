"""Uniform weight crossover helpers for H-XOV."""

from __future__ import annotations

import random
from typing import Any

import torch


def blend_state_dicts(
    a: dict[str, torch.Tensor],
    b: dict[str, torch.Tensor],
    rng: random.Random,
) -> dict[str, torch.Tensor]:
    """
    GIVEN two state_dicts with matching keys
    WHEN blending uniformly
    THEN each floating tensor is cloned from a or b with p=0.5;
    non-float tensors are cloned from a.
    """
    if a.keys() != b.keys():
        raise ValueError("blend_state_dicts: key mismatch")
    out: dict[str, torch.Tensor] = {}
    for k, va in a.items():
        vb = b[k]
        if va.dtype.is_floating_point and rng.random() < 0.5:
            out[k] = vb.clone()
        else:
            out[k] = va.clone()
    return out


def pick_parent_pair(
    n_parents: int, rng: random.Random
) -> tuple[int, int]:
    """
    GIVEN number of truncation parents
    WHEN picking a mating pair
    THEN return two indices in [0, n_parents); allow same parent (self-blend).
    """
    if n_parents < 1:
        raise ValueError("pick_parent_pair: need >= 1 parents")
    return rng.randrange(n_parents), rng.randrange(n_parents)


def pop_diversity(states: list[dict[str, Any]]) -> float:
    """Mean pairwise L2 over flattened float tensors (CPU)."""
    if len(states) < 2:
        return 0.0
    vecs = []
    for st in states:
        parts = [
            v.detach().float().reshape(-1).cpu()
            for v in st.values()
            if v.dtype.is_floating_point
        ]
        vecs.append(torch.cat(parts))
    total = 0.0
    n = 0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            total += float(torch.norm(vecs[i] - vecs[j]).item())
            n += 1
    return total / max(n, 1)
