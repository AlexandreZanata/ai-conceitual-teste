"""TinyStories token batches for student training (smoke-friendly)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import torch
from datasets import load_dataset


def load_tokenizer(tokenizer_id: str, cache_dir: Path | None):
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(
        tokenizer_id, cache_dir=str(cache_dir) if cache_dir else None
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def iter_token_batches(
    tokenizer,
    *,
    cache_dir: Path | None,
    max_examples: int,
    seq_len: int,
    batch_size: int,
    device: torch.device,
) -> Iterator[torch.Tensor]:
    """Yield input_ids [B, T] from TinyStories text (truncated)."""
    ds = load_dataset(
        "roneneldan/TinyStories",
        split="train",
        streaming=True,
        cache_dir=str(cache_dir) if cache_dir else None,
    )
    buf: list[int] = []
    seen = 0
    batch: list[list[int]] = []
    for row in ds:
        if seen >= max_examples:
            break
        text = row.get("text") or ""
        if not text.strip():
            continue
        ids = tokenizer.encode(text, add_special_tokens=False)
        buf.extend(ids + [tokenizer.eos_token_id])
        seen += 1
        while len(buf) >= seq_len:
            chunk = buf[:seq_len]
            buf = buf[seq_len:]
            batch.append(chunk)
            if len(batch) >= batch_size:
                yield torch.tensor(batch, dtype=torch.long, device=device)
                batch = []
    if batch:
        yield torch.tensor(batch, dtype=torch.long, device=device)
