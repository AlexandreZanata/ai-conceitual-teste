"""H-HALF: fp16-wire topk_val H2D under PRE; ms/step vs H-PRE."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hhalf", "to_device_rec_half", "EPS_LP"]


def to_device_rec_half(
    rec: dict,
    *,
    device,
    vocab_size: int,
    non_blocking: bool,
) -> tuple:
    """
    GIVEN pinned top-k cache record
    WHEN H2D keeps topk_val fp16 then cast on GPU before expand
    THEN return (ids, dense teacher logits fp32).
    """
    import torch

    from top_ops import expand_topk_logits

    ids = rec["ids"].to(device, non_blocking=non_blocking)
    idx = rec["topk_idx"].to(device, non_blocking=non_blocking)
    val_h = rec["topk_val"].to(device=device, non_blocking=non_blocking)
    if val_h.dtype != torch.float16:
        val_h = val_h.to(dtype=torch.float16)
    return ids, expand_topk_logits(idx, val_h.float(), vocab_size=vocab_size)


def decide_hhalf(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-HALF vs H-PRE
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and ms/step < PRE; else KILL.
    """
    tip = stats.get("H-PRE")
    if tip is None:
        return "needs H-PRE control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-PRE)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-PRE)"
    return "PROMOTE (fp16-wire H2D under PRE)"
