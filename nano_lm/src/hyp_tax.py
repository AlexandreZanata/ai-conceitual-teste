"""H-TAX: H-SEL scaffold; scale elite weights ×(1−τ) each generation."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from student_model import build_student, count_params
from tax_ops import apply_wealth_tax, elite_indices
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_tax(
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
    tau: float = 0.05,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
    elite_k = max(1, pop_size // 2)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
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
        raise RuntimeError("H-TAX: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    taxed_log: list[list[int]] = []
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        top = max(range(pop_size), key=lambda i: fits[i])
        history.append(fits[top])
        if fits[top] > best_fit:
            best_fit = fits[top]
            best_state = copy.deepcopy(pop[top].state_dict())
        taxed = elite_indices(fits, elite_k)
        taxed_log.append(taxed)
        for i in taxed:
            taxed_sd = apply_wealth_tax(pop[i].state_dict(), tau)
            pop[i].load_state_dict(taxed_sd)
            pop[i].eval()
        parents = [pop[i] for i in taxed]
        new_pop = []
        for i in range(pop_size):
            child = build_student(vocab).to(device)
            src = parents[i % len(parents)].state_dict()
            child.load_state_dict(mutate_state(src, mutate_scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-TAX",
        "tau": tau,
        "elite_k": elite_k,
        "taxed_per_gen": taxed_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
