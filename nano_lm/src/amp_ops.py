"""H-AMP: CUDA AMP dtype + dual gate vs H-EARLY (quality@wall)."""

from __future__ import annotations

from typing import Mapping

import torch

from lat_ops import EPS_LP

__all__ = [
    "AMP_KINDS",
    "resolve_amp_dtype",
    "cast_student_amp",
    "decide_hamp",
    "EPS_LP",
]

AMP_KINDS = ("bf16", "fp16", "fp32")


def resolve_amp_dtype(kind: str, device: torch.device) -> torch.dtype:
    """
    GIVEN amp kind and device
    WHEN resolving
    THEN bf16 if supported on CUDA; else fp16 on CUDA; fp32 on CPU/fallback.
    """
    k = str(kind).lower().strip()
    if k not in AMP_KINDS:
        raise ValueError(f"unknown amp kind: {kind}")
    if device.type != "cuda" or k == "fp32":
        return torch.float32
    if k == "bf16":
        if torch.cuda.is_bf16_supported():
            return torch.bfloat16
        return torch.float16
    return torch.float16


def cast_student_amp(student: object, dtype: torch.dtype) -> object:
    """
    GIVEN a student module
    WHEN casting for AMP decode
    THEN return eval module in dtype (in-place cast).
    """
    student.to(dtype=dtype)
    student.eval()
    return student


def decide_hamp(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-AMP vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and wall < EARLY; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-EARLY)"
    return "PROMOTE (AMP vs EARLY)"
