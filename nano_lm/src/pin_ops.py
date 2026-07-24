"""H-PIN: pinned + non_blocking H2D for TOP cache tensors."""

from __future__ import annotations

from typing import Mapping, Sequence

from lat_ops import EPS_LP

__all__ = ["pin_records", "decide_hpin", "EPS_LP"]


def pin_records(records: Sequence[dict]) -> list[dict]:
    """
    GIVEN CPU top-k cache records
    WHEN preparing for async H2D
    THEN return pinned contiguous copies of ids/idx/val.
    """
    out: list[dict] = []
    for rec in records:
        out.append(
            {
                "ids": rec["ids"].contiguous().pin_memory(),
                "topk_idx": rec["topk_idx"].contiguous().pin_memory(),
                "topk_val": rec["topk_val"].contiguous().pin_memory(),
            }
        )
    return out


def decide_hpin(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-PIN vs H-TOP tip (same cache)
    WHEN deciding
    THEN PROMOTE iff lp ≥ TOP−ε and ms/step < TOP; else KILL.
    """
    tip = stats.get("H-TOP")
    if tip is None:
        return "needs H-TOP control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-TOP)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-TOP)"
    return "PROMOTE (pinned H2D vs TOP)"
