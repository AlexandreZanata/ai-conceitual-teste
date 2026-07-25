"""Single-batch top-k teacher cache record (for async pipeline)."""

from __future__ import annotations

import torch

__all__ = ["build_one_topk"]


def build_one_topk(
    teacher: object,
    ids_cpu: torch.Tensor,
    *,
    top_k: int,
) -> dict[str, torch.Tensor]:
    """
    GIVEN one id batch and loaded teacher
    WHEN computing top-k logits
    THEN return CPU record {ids, topk_idx int32, topk_val fp16}.
    """
    if int(top_k) < 1:
        raise ValueError("top_k must be >= 1")
    device = teacher.device  # type: ignore[attr-defined]
    with torch.no_grad():
        ids = ids_cpu.to(device, non_blocking=device.type == "cuda")
        logits = teacher.model(ids).logits  # type: ignore[attr-defined]
        vals, idxs = torch.topk(logits.float(), k=int(top_k), dim=-1)
        rec = {
            "ids": ids_cpu.contiguous(),
            "topk_idx": idxs.detach().to(dtype=torch.int32).cpu().contiguous(),
            "topk_val": vals.detach().to(dtype=torch.float16).cpu().contiguous(),
        }
    return rec
