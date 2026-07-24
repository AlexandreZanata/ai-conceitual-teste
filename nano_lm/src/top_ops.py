"""H-TOP: top-k offline soft-label cache; train step-time gate vs live STAG."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from soft_ops import ms_per_step

__all__ = ["DEFAULT_TOP_K", "decide_htop", "ms_per_step", "expand_topk_logits"]

DEFAULT_TOP_K = 64


def expand_topk_logits(
    indices,  # torch.Tensor [B,T,K]
    values,  # torch.Tensor [B,T,K]
    *,
    vocab_size: int,
    fill: float = -1.0e4,
):
    """
    GIVEN top-k indices and values
    WHEN reconstructing dense teacher logits
    THEN scatter values into a filled tensor of size vocab_size.
    """
    import torch

    b, t, k = indices.shape
    out = torch.full(
        (b, t, int(vocab_size)),
        float(fill),
        dtype=torch.float32,
        device=indices.device,
    )
    out.scatter_(-1, indices.long(), values.float())
    return out


def decide_htop(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-TOP vs live H-STAG control
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and ms/step < STAG; else KILL.
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-STAG)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs live STAG)"
    return "PROMOTE (top-k soft cache vs live STAG)"
