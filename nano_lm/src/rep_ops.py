"""H-REP: repetition-penalty decode helpers; dual gate vs B4."""

from __future__ import annotations

from typing import Mapping, Sequence

import torch

from lat_ops import EPS_LP

__all__ = [
    "PENALTIES",
    "apply_rep_penalty",
    "decide_hrep",
]

PENALTIES = (1.0, 1.1, 1.2, 1.35)


def apply_rep_penalty(
    logits: torch.Tensor, prev_ids: torch.Tensor, penalty: float
) -> torch.Tensor:
    """
    GIVEN logits [B,V] and previous token ids [B,T]
    WHEN applying HF-style repetition penalty
    THEN downscale seen tokens (score>0 ÷p, score<0 ×p); p=1 is identity.
    """
    p = float(penalty)
    if p < 1.0:
        raise ValueError("apply_rep_penalty: penalty must be >= 1")
    if abs(p - 1.0) < 1e-9:
        return logits
    out = logits.clone()
    for b in range(int(out.shape[0])):
        seen = set(int(x) for x in prev_ids[b].tolist())
        for tid in seen:
            if float(out[b, tid]) > 0.0:
                out[b, tid] = out[b, tid] / p
            else:
                out[b, tid] = out[b, tid] * p
    return out


def decide_hrep(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-REP vs B4
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


def best_penalty_index(scores: Sequence[float]) -> int:
    """Argmax over grid scores; ties keep lowest index."""
    if not scores:
        raise ValueError("best_penalty_index: empty")
    best_i = 0
    best_v = float(scores[0])
    for i in range(1, len(scores)):
        v = float(scores[i])
        if v > best_v:
            best_i = i
            best_v = v
    return best_i
