"""H-FOS: H-SEL scaffold; fossil vault resurrects extinct lineage every K gens."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from fos_ops import should_resurrect, vault_pop, vault_push, worst_index
from hyp_sel import mutate_state
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_fos(
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
    resurrect_every: int = 2,
    vault_max: int = 8,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
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
        raise RuntimeError("H-FOS: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    vault: list[dict[str, Any]] = []
    resurrect_log: list[dict[str, int]] = []
    for gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parent_n = max(1, pop_size // 2)
        parents = [pop[i] for i in ranked[:parent_n]]
        for i in ranked[parent_n:]:
            vault_push(
                vault,
                copy.deepcopy(pop[i].state_dict()),
                fits[i],
                max_size=vault_max,
            )
        new_pop = []
        for i in range(pop_size):
            child = build_student(vocab).to(device)
            src = parents[i % len(parents)].state_dict()
            child.load_state_dict(mutate_state(src, mutate_scale))
            child.eval()
            new_pop.append(child)
        if should_resurrect(gen, resurrect_every) and vault:
            fossil = vault_pop(vault)
            slot = worst_index([_fitness(m, probe) for m in new_pop])
            new_pop[slot].load_state_dict(fossil["state"])
            new_pop[slot].eval()
            resurrect_log.append({"gen": gen, "slot": slot})
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-FOS",
        "resurrect_every": resurrect_every,
        "vault_max": vault_max,
        "resurrect_log": resurrect_log,
        "vault_final": len(vault),
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
