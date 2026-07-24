"""H-COMP: torch.compile decode on frozen EARLY tip genes."""

from __future__ import annotations

from typing import Any, Mapping

import torch

from lat_ops import EPS_LP

__all__ = [
    "EPS_LP",
    "COMPILE_MODE",
    "compile_student",
    "warmup_student",
    "decide_hcomp",
]

COMPILE_MODE = "reduce-overhead"


def compile_student(model: Any, *, mode: str = COMPILE_MODE) -> Any:
    """
    GIVEN an eager student
    WHEN compiling for inference
    THEN return torch.compile wrapper (CUDA graphs via reduce-overhead).
    """
    return torch.compile(model, mode=mode)


def warmup_student(model: Any, device: torch.device, *, steps: int = 3) -> None:
    """Run cheap forwards so compile/CUDA-graph capture is paid before timing."""
    ids = torch.randint(0, 128, (1, 8), device=device)
    with torch.no_grad():
        for _ in range(max(1, int(steps))):
            model(ids)
    if device.type == "cuda":
        torch.cuda.synchronize()


def decide_hcomp(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-COMP vs H-EARLY (same genes/ckpt)
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
    return "PROMOTE (torch.compile vs H-EARLY)"
