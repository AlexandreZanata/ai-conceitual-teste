"""H-Q8: INT8 dynamic quant inference on CURL + EARLY genes."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn as nn
from torch.ao.quantization import quantize_dynamic

from lat_ops import EPS_LP

__all__ = ["EPS_LP", "quantize_student_dynamic", "decide_hq8", "has_dynamic_linear"]


def quantize_student_dynamic(model: nn.Module) -> nn.Module:
    """
    GIVEN a trained student
    WHEN applying inference-only dynamic INT8
    THEN Linear layers use qint8 dynamic kernels (CPU backend).
    """
    cpu = model.cpu().float().eval()
    return quantize_dynamic(cpu, {nn.Linear}, dtype=torch.qint8)


def has_dynamic_linear(model: nn.Module) -> bool:
    """True if at least one packed dynamic Linear is present."""
    for mod in model.modules():
        name = type(mod).__name__
        if "Dynamic" in name and "Linear" in name:
            return True
        if name == "LinearPackedParams":
            return True
    return False


def decide_hq8(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-Q8 vs H-CURL on same EARLY decode
    WHEN deciding
    THEN PROMOTE iff lp ≥ CURL−ε and wall < CURL; else KILL.
    """
    tip = stats.get("H-CURL")
    if tip is None:
        return "needs H-CURL control (same EARLY decode)"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-CURL)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-CURL)"
    return "PROMOTE (INT8 dynamic + EARLY vs tip)"
