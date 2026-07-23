"""Ablate H-SUP / H-INT vs uniform BoN on shared candidate scores."""

from __future__ import annotations

from typing import Any

import torch

from decode_ar import sample_next_batch
from hyp_quantum import select_int, select_sup, select_uniform_bon
from load_model import LoadedModel


def _candidate_scores(
    model,
    prompt_ids: torch.Tensor,
    *,
    k: int,
    max_new: int,
    temperature: float,
    top_p: float,
    device: torch.device,
) -> tuple[list[float], torch.Tensor]:
    """Return mean logprobs [K] and last-token embeddings proxy [K, H]."""
    ids = prompt_ids.repeat(k, 1)
    lps = torch.zeros(k, max_new, device=device)
    for step in range(max_new):
        tok, lp, _ = sample_next_batch(
            model, ids, temperature=temperature, top_p=top_p
        )
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
    scores = lps.mean(dim=1).tolist()
    with torch.no_grad():
        # use logits as cheap embedding proxy [K, V] → project via mean pool chunks
        logits = model(ids).logits[:, -1, :].float()
        # reduce V → D by reshape avg
        d = 64
        v = logits.shape[-1]
        usable = (v // d) * d
        emb = logits[:, :usable].view(k, -1, d).mean(dim=1)
    return scores, emb


def run_quantum_ablation(
    loaded: LoadedModel,
    prompt: str,
    *,
    k: int,
    max_new: int,
    temperature: float,
    top_p: float,
    seed: int,
) -> dict[str, Any]:
    tok = loaded.tokenizer
    device = loaded.device
    prompt_ids = tok.encode(prompt, return_tensors="pt").to(device)
    torch.manual_seed(seed)
    scores, emb = _candidate_scores(
        loaded.model,
        prompt_ids,
        k=k,
        max_new=max_new,
        temperature=temperature,
        top_p=top_p,
        device=device,
    )
    return {
        "uniform_bon": select_uniform_bon(scores),
        "h_sup": select_sup(scores, seed),
        "h_int": select_int(scores, emb, seed),
        "scores": scores,
        "best_score": max(scores),
        "sup_score": scores[select_sup(scores, seed)],
        "int_score": scores[select_int(scores, emb, seed)],
        "bon_score": scores[select_uniform_bon(scores)],
    }
