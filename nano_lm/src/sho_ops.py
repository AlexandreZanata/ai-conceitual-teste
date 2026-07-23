"""Shock helpers for H-SHO: reinit one layer of a mutated child state."""

from __future__ import annotations

from typing import Mapping

import torch


def layer_prefixes(keys: list[str]) -> list[str]:
    """
    GIVEN state_dict keys
    WHEN grouping into reinitable layers
    THEN return sorted unique prefixes (block / embed / head).
    """
    out: set[str] = set()
    for k in keys:
        parts = k.split(".")
        if len(parts) >= 3 and parts[0] == "transformer" and parts[1] == "h":
            out.add(".".join(parts[:3]))
        elif len(parts) >= 2 and parts[0] == "transformer":
            out.add(".".join(parts[:2]))
        else:
            out.add(parts[0])
    return sorted(out)


def keys_for_prefix(keys: list[str], prefix: str) -> list[str]:
    """Keys belonging to prefix (exact or prefix.)."""
    return [k for k in keys if k == prefix or k.startswith(prefix + ".")]


def shock_state(
    state: Mapping[str, torch.Tensor],
    fresh: Mapping[str, torch.Tensor],
    prefix: str,
) -> dict[str, torch.Tensor]:
    """
    GIVEN mutated state, a freshly init state, and a layer prefix
    WHEN applying shock
    THEN copy fresh tensors for that layer; leave others from state.
    """
    if not prefix:
        raise ValueError("shock_state: empty prefix")
    out: dict[str, torch.Tensor] = {}
    hit = 0
    for k, v in state.items():
        if k == prefix or k.startswith(prefix + "."):
            if k not in fresh:
                raise KeyError(f"shock_state: missing fresh key {k}")
            out[k] = fresh[k].detach().clone()
            hit += 1
        else:
            out[k] = v.detach().clone() if isinstance(v, torch.Tensor) else v
    if hit == 0:
        raise ValueError(f"shock_state: no keys for prefix {prefix}")
    return out


def pick_prefix(prefixes: list[str], index: int) -> str:
    """Pick prefix by non-negative index mod len."""
    if not prefixes:
        raise ValueError("pick_prefix: empty")
    if index < 0:
        raise ValueError("pick_prefix: index must be >= 0")
    return prefixes[index % len(prefixes)]
