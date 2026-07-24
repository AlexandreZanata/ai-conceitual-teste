"""Build offline top-k teacher logit cache (k ≪ V)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch


def build_topk_cache(
    *,
    teacher: object,
    batches: list[torch.Tensor],
    out_path: Path,
    top_k: int,
) -> dict[str, Any]:
    """
    GIVEN planned id batches and a loaded teacher
    WHEN precomputing top-k logits once
    THEN save (ids, topk_idx int32, topk_val fp16) on CPU.
    """
    if int(top_k) < 1:
        raise ValueError("top_k must be >= 1")
    device = teacher.device  # type: ignore[attr-defined]
    records: list[dict[str, torch.Tensor]] = []
    t0 = time.perf_counter()
    with torch.no_grad():
        for ids_cpu in batches:
            ids = ids_cpu.to(device)
            logits = teacher.model(ids).logits  # type: ignore[attr-defined]
            vals, idxs = torch.topk(logits.float(), k=int(top_k), dim=-1)
            records.append(
                {
                    "ids": ids_cpu,
                    "topk_idx": idxs.detach().to(dtype=torch.int32).cpu().contiguous(),
                    "topk_val": vals.detach().to(dtype=torch.float16).cpu().contiguous(),
                }
            )
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_s = time.perf_counter() - t0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"records": records, "n": len(records), "top_k": int(top_k)}, out_path
    )
    return {
        "cache_path": str(out_path),
        "n_batches": len(records),
        "cache_build_s": wall_s,
        "top_k": int(top_k),
    }


def load_topk_cache(path: Path) -> tuple[list[dict[str, torch.Tensor]], int]:
    try:
        blob = torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        blob = torch.load(path, map_location="cpu")
    return list(blob["records"]), int(blob.get("top_k", 0))
