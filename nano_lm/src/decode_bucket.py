"""Length-bucketed multi-prompt EARLY decode (pad within band only)."""

from __future__ import annotations

from typing import Any

import torch

from bucket_ops import DEFAULT_BAND, assign_length_buckets
from decode_bat import decode_early_batch
from scorers import DecodeResult


def decode_early_bucketed(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    n: int,
    max_new_tokens: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
    band: int = DEFAULT_BAND,
) -> tuple[list[DecodeResult], float, int]:
    """
    GIVEN prompts of mixed lengths
    WHEN decoding in length bands
    THEN left-pad only within each band; return results in prompt order.
    """
    if not prompts:
        raise ValueError("prompts must be non-empty")
    raw = [tokenizer.encode(p, add_special_tokens=False) for p in prompts]
    lengths = [len(s) for s in raw]
    groups = assign_length_buckets(lengths, band=band)
    out: list[DecodeResult | None] = [None] * len(prompts)
    wall_sum = 0.0
    for gi, idxs in enumerate(groups):
        sub = [prompts[i] for i in idxs]
        results, wall_ms = decode_early_batch(
            model,
            tokenizer,
            sub,
            n=n,
            max_new_tokens=max_new_tokens,
            min_new=min_new,
            conf_threshold=conf_threshold,
            patience=patience,
            temperature=temperature,
            top_p=top_p,
            seed=seed + 17 * gi,
            device=device,
        )
        wall_sum += float(wall_ms)
        for local, global_i in enumerate(idxs):
            out[global_i] = results[local]
    assert all(r is not None for r in out)
    return [r for r in out if r is not None], wall_sum, len(groups)
