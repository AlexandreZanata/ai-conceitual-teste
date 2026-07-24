"""H-MINP: min-p sampling helpers; dual gate vs B4."""

from __future__ import annotations

from typing import Mapping, Sequence

import torch
import torch.nn.functional as F

from lat_ops import EPS_LP

__all__ = [
    "MIN_PS",
    "apply_min_p",
    "decide_hminp",
    "best_minp_index",
]

# 0 = identity (no min-p filter).
MIN_PS = (0.0, 0.05, 0.1, 0.2)


def apply_min_p(logits: torch.Tensor, min_p: float) -> torch.Tensor:
    """
    GIVEN logits [B,V] and min_p in [0,1)
    WHEN filtering
    THEN keep tokens with p ≥ min_p·max_p; min_p=0 is identity.
    """
    mp = float(min_p)
    if not (0.0 <= mp < 1.0):
        raise ValueError("apply_min_p: min_p must be in [0,1)")
    if mp == 0.0:
        return logits
    probs = F.softmax(logits.float(), dim=-1)
    thresh = mp * probs.max(dim=-1, keepdim=True).values
    out = logits.clone()
    out = out.masked_fill(probs < thresh, float("-inf"))
    return out


def decide_hminp(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-MINP vs B4
    WHEN deciding
    THEN PROMOTE only if quality ≥ B4−ε and wall < B4; else KILL.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s["mean_lp"]) < float(b4["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs B4)"
    if not (float(s["mean_wall"]) < float(b4["mean_wall"])):
        return "KILL (no speedup vs B4)"
    return "PROMOTE (quality@wall vs B4)"


def best_minp_index(scores: Sequence[float]) -> int:
    """Argmax over grid scores; ties keep lowest index."""
    if not scores:
        raise ValueError("best_minp_index: empty")
    best_i = 0
    best_v = float(scores[0])
    for i in range(1, len(scores)):
        v = float(scores[i])
        if v > best_v:
            best_i = i
            best_v = v
    return best_i
