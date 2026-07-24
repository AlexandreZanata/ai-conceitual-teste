"""Plan curriculum batches + build offline teacher logit cache."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch

from cur_ops import cur_seq_len
from data_tiny import load_tokenizer
from hyp_cur import _make_data, _next_batch


def plan_cur_batches(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    steps: int,
    batch_size: int,
    seq_len: int,
    max_examples: int,
    seq_lo: int,
    n_stages: int,
    seed: int,
) -> list[torch.Tensor]:
    """
    GIVEN STAG curriculum knobs
    WHEN planning train batches
    THEN return CPU int64 ids [B,T] per step (deterministic seed).
    """
    torch.manual_seed(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    device = torch.device("cpu")
    cur = cur_seq_len(0, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages)
    data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
    out: list[torch.Tensor] = []
    for step in range(steps):
        want = cur_seq_len(
            step, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages
        )
        if want != cur:
            cur = want
            data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
        ids, data = _next_batch(
            data, tok, cache_dir, max_examples, cur, batch_size, device
        )
        out.append(ids.detach().cpu().contiguous())
    return out


def build_soft_cache(
    *,
    teacher: object,
    batches: list[torch.Tensor],
    out_path: Path,
) -> dict[str, Any]:
    """
    GIVEN planned id batches and a loaded teacher
    WHEN precomputing teacher logits once
    THEN save fp16 logits on CPU and return build meta.
    """
    device = teacher.device  # type: ignore[attr-defined]
    records: list[dict[str, torch.Tensor]] = []
    t0 = time.perf_counter()
    with torch.no_grad():
        for ids_cpu in batches:
            ids = ids_cpu.to(device)
            logits = (
                teacher.model(ids)  # type: ignore[attr-defined]
                .logits.detach()
                .to(dtype=torch.float16)
                .cpu()
            )
            records.append({"ids": ids_cpu, "logits": logits.contiguous()})
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_s = time.perf_counter() - t0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"records": records, "n": len(records)}, out_path)
    return {
        "cache_path": str(out_path),
        "n_batches": len(records),
        "cache_build_s": wall_s,
    }


def load_soft_cache(path: Path) -> list[dict[str, torch.Tensor]]:
    try:
        blob = torch.load(path, map_location="cpu", weights_only=False)
    except TypeError:
        blob = torch.load(path, map_location="cpu")
    return list(blob["records"])
