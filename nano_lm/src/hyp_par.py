"""H-PAR: H-SEL scaffold; parasite vector steals selection fitness credit."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from par_ops import (
    mutate_parasite,
    parents_diverge,
    parasite_claim,
    selection_fitness,
    top_half_indices,
)
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_par(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    mutate_scale: float,
    seq_len: int,
    batch_size: int,
    max_examples: int,
    seed: int,
    out_path: Path,
    steal_alpha: float = 0.5,
    parasite_dim: int = 16,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    parasites = [torch.randn(parasite_dim) for _ in range(pop_size)]
    for m in pop:
        m.eval()
    data = list(
        iter_token_batches(
            tok,
            cache_dir=cache_dir,
            max_examples=max_examples,
            seq_len=seq_len,
            batch_size=batch_size,
            device=device,
        )
    )
    if not data:
        raise RuntimeError("H-PAR: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    claims_log: list[list[float]] = []
    diverge_gens = 0
    for _gen in range(generations):
        host_fits = [_fitness(m, probe) for m in pop]
        claims = [parasite_claim(p, steal_alpha) for p in parasites]
        sel_fits = [selection_fitness(h, c) for h, c in zip(host_fits, claims)]
        claims_log.append(claims)
        if parents_diverge(host_fits, sel_fits):
            diverge_gens += 1
        top = max(range(pop_size), key=lambda i: host_fits[i])
        history.append(host_fits[top])
        if host_fits[top] > best_fit:
            best_fit = host_fits[top]
            best_state = copy.deepcopy(pop[top].state_dict())
        parent_idx = top_half_indices(sel_fits)
        new_pop, new_par = [], []
        for i in range(pop_size):
            src_i = parent_idx[i % len(parent_idx)]
            child = build_student(vocab).to(device)
            child.load_state_dict(mutate_state(pop[src_i].state_dict(), mutate_scale))
            child.eval()
            new_pop.append(child)
            new_par.append(mutate_parasite(parasites[src_i], mutate_scale))
        pop, parasites = new_pop, new_par
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    diverge_rate = diverge_gens / max(generations, 1)
    return {
        "hypothesis": "H-PAR",
        "steal_alpha": steal_alpha,
        "parasite_dim": parasite_dim,
        "claims_per_gen": claims_log,
        "diverge_rate": diverge_rate,
        "parasite_dominates": diverge_rate > 0.5,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
