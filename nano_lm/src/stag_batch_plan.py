"""Plan STAG curriculum CPU id batches (shared by H-TOP live control)."""

from __future__ import annotations

from pathlib import Path

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
