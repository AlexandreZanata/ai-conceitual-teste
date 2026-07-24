"""Build teacher-NLL-sorted chunk pools for H-CURD."""

from __future__ import annotations

from typing import Any

import torch

from data_tiny import iter_token_batches
from train_ce import ce_loss


def collect_chunks(
    tok: Any,
    *,
    cache_dir,
    max_examples: int,
    seq_len: int,
    batch_size: int,
    device: torch.device,
) -> list[torch.Tensor]:
    """Return CPU [T] chunks at fixed seq_len."""
    chunks: list[torch.Tensor] = []
    for batch in iter_token_batches(
        tok,
        cache_dir=cache_dir,
        max_examples=max_examples,
        seq_len=seq_len,
        batch_size=batch_size,
        device=device,
    ):
        for i in range(int(batch.shape[0])):
            chunks.append(batch[i].detach().cpu())
    if not chunks:
        raise RuntimeError("collect_chunks: empty pool")
    return chunks


def score_nll(teacher: Any, chunk: torch.Tensor, device: torch.device) -> float:
    """Teacher CE/NLL of one chunk (higher = harder)."""
    ids = chunk.unsqueeze(0).to(device)
    with torch.no_grad():
        logits = teacher.model(ids).logits
        return float(ce_loss(logits, ids).item())


def sort_easy_first(
    teacher: Any, chunks: list[torch.Tensor], device: torch.device
) -> list[torch.Tensor]:
    scored = [(score_nll(teacher, c, device), c) for c in chunks]
    scored.sort(key=lambda x: x[0])
    return [c for _, c in scored]


def batch_from_pool(
    pool: list[torch.Tensor],
    *,
    start: int,
    batch_size: int,
    device: torch.device,
) -> tuple[torch.Tensor, int]:
    """Cycle pool from start; return (ids [B,T], next_index)."""
    n = len(pool)
    rows = [pool[(start + i) % n].to(device) for i in range(batch_size)]
    return torch.stack(rows, dim=0), (start + batch_size) % n
