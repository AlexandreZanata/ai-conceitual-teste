"""H-TYP: typical sampling helpers; dual gate vs B4."""

from __future__ import annotations

from typing import Mapping, Sequence

import torch
import torch.nn.functional as F

from lat_ops import EPS_LP

__all__ = [
    "TYP_MASSES",
    "apply_typical",
    "decide_htyp",
    "best_typ_index",
]

# 1.0 = identity (keep full mass).
TYP_MASSES = (1.0, 0.9, 0.8, 0.7)


def apply_typical(logits: torch.Tensor, mass: float) -> torch.Tensor:
    """
    GIVEN logits [B,V] and mass in (0,1]
    WHEN filtering by typicality (HF-style)
    THEN keep a mass-prefix of tokens closest to local entropy; mass=1 is identity.
    """
    m = float(mass)
    if not (0.0 < m <= 1.0):
        raise ValueError("apply_typical: mass must be in (0,1]")
    if abs(m - 1.0) < 1e-9:
        return logits
    probs = F.softmax(logits.float(), dim=-1)
    log_p = torch.log(probs.clamp_min(1e-12))
    ent = -(probs * log_p).sum(dim=-1, keepdim=True)
    shifted = torch.abs(-log_p - ent)
    sorted_shift, sorted_idx = torch.sort(shifted, dim=-1)
    sorted_probs = probs.gather(-1, sorted_idx)
    cum = torch.cumsum(sorted_probs, dim=-1)
    # Keep until cum reaches mass (first index with cum >= mass).
    mask_sorted = cum > m
    mask_sorted[..., 1:] = mask_sorted[..., :-1].clone()
    mask_sorted[..., 0] = False
    out = logits.clone()
    ban = torch.zeros_like(probs, dtype=torch.bool)
    ban.scatter_(-1, sorted_idx, mask_sorted)
    out = out.masked_fill(ban, float("-inf"))
    return out


def decide_htyp(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-TYP vs B4
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


def best_typ_index(scores: Sequence[float]) -> int:
    """Argmax over grid scores; ties keep lowest index."""
    if not scores:
        raise ValueError("best_typ_index: empty")
    best_i = 0
    best_v = float(scores[0])
    for i in range(1, len(scores)):
        v = float(scores[i])
        if v > best_v:
            best_i = i
            best_v = v
    return best_i
