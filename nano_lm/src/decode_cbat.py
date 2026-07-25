"""Batched EARLY decode with chunked KV prefill (block size B)."""

from __future__ import annotations

import time
from typing import Any

import torch

from bat_ops import left_pad_batch
from cbat_steps import generate_chunked, prefill_chunked
from scorers import DecodeResult, mean_logprob, pick_argmax


def decode_early_batch_chunked(
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
    chunk_size: int,
) -> tuple[list[DecodeResult], float]:
    """
    GIVEN many prompts, EARLY genes, chunk_size B
    WHEN left-pad batch, prefill in blocks of B with KV, then generate
    THEN return per-prompt best-of-n results and shared wall_ms.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if int(chunk_size) < 1:
        raise ValueError("chunk_size must be >= 1")
    if not prompts:
        raise ValueError("prompts must be non-empty")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    pad_id = int(tokenizer.pad_token_id)
    raw = [tokenizer.encode(p, add_special_tokens=False) for p in prompts]
    expanded: list[list[int]] = []
    owners: list[int] = []
    for pi, seq in enumerate(raw):
        for _ in range(n):
            expanded.append(list(seq))
            owners.append(pi)
    padded, masks, prompt_lens = left_pad_batch(expanded, pad_id=pad_id)
    ids = torch.tensor(padded, dtype=torch.long, device=device)
    mask = torch.tensor(masks, dtype=torch.long, device=device)
    bsz = ids.shape[0]
    prompt_len = int(ids.shape[1])
    t0 = time.perf_counter()
    logits, past, token_evals = prefill_chunked(
        model, ids, mask, chunk_size=int(chunk_size)
    )
    ids, mask, lps, gen, stop_at, token_evals = generate_chunked(
        model,
        tokenizer,
        ids=ids,
        mask=mask,
        logits=logits,
        past=past,
        bsz=bsz,
        max_new_tokens=max_new_tokens,
        min_new=min_new,
        conf_threshold=conf_threshold,
        patience=patience,
        temperature=temperature,
        top_p=top_p,
        token_evals=token_evals,
    )
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    results = _pack(
        tokenizer,
        prompts,
        owners,
        ids,
        lps,
        prompt_lens,
        stop_at,
        gen,
        wall_ms,
        token_evals,
        prompt_len=prompt_len,
    )
    return results, wall_ms


def _pack(
    tokenizer: Any,
    prompts: list[str],
    owners: list[int],
    ids: torch.Tensor,
    lps: torch.Tensor,
    prompt_lens: list[int],
    stop_at: list[int],
    gen: int,
    wall_ms: float,
    token_evals: int,
    *,
    prompt_len: int,
) -> list[DecodeResult]:
    out: list[DecodeResult] = []
    for pi in range(len(prompts)):
        idxs = [i for i, o in enumerate(owners) if o == pi]
        means = [mean_logprob(lps[i, : stop_at[i]].tolist()) for i in idxs]
        best_local = pick_argmax(means)
        bi = idxs[best_local]
        plen = prompt_lens[bi]
        full = ids[bi].tolist()
        pad = prompt_len - plen
        end = pad + plen + stop_at[bi]
        new_ids = tuple(int(x) for x in full[pad + plen : end])
        text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
        out.append(
            DecodeResult(
                token_ids=new_ids,
                text=text,
                mean_logprob=means[best_local],
                wall_ms=wall_ms,
                token_evals=token_evals // max(len(prompts), 1),
            )
        )
    return out
