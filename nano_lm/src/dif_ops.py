"""H-DIF: discrete diffusion helpers; decide vs B2 on quality/slow/VRAM."""

from __future__ import annotations

from typing import Mapping

import torch

__all__ = [
    "VRAM_STOP_MIB",
    "SLOW_RATIO",
    "corrupt_tokens",
    "decide_hdif",
]

VRAM_STOP_MIB = 7.0 * 1024.0
SLOW_RATIO = 2.0


def corrupt_tokens(
    ids: torch.Tensor,
    *,
    rate: float,
    mask_id: int,
    generator: torch.Generator | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """
    GIVEN clean token ids and corruption rate in [0,1]
    WHEN applying absorbing-state noise
    THEN return (noisy_ids, bool mask of corrupted positions).
    """
    if not (0.0 <= float(rate) <= 1.0):
        raise ValueError("corrupt_tokens: rate must be in [0,1]")
    # CPU generator + .to(device): PyTorch forbids mixed CPU/CUDA generators.
    if generator is None:
        noise = torch.rand(ids.shape, device=ids.device) < float(rate)
    else:
        noise = (torch.rand(ids.shape, generator=generator) < float(rate)).to(
            ids.device
        )
    out = ids.clone()
    out[noise] = int(mask_id)
    return out, noise


def decide_hdif(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DIF vs B2
    WHEN deciding
    THEN KILL on VRAM stop, wall > SLOW_RATIO×B2, or ≤ B2; else PROMOTE.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s.get("peak_vram_mib", 0.0)) > VRAM_STOP_MIB:
        return "KILL (VRAM)"
    b2_wall = float(b2.get("mean_wall", float("nan")))
    if b2_wall == b2_wall and float(s["mean_wall"]) > SLOW_RATIO * b2_wall:
        return "KILL (too slow)"
    if float(s["mean_lp"]) <= float(b2["mean_lp"]) + 1e-6:
        return "KILL (≤ B2)"
    return "PROMOTE (beats B2 @ cost)"
