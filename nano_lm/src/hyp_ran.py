"""H-RAN: H-SEL scaffold; linear rank roulette instead of truncation."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from ran_ops import linear_ranks, select_parents_rank
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_ran(
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
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    rng = random.Random(seed)
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
        raise RuntimeError("H-RAN: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    parent_log: list[list[int]] = []
    rank_log: list[list[int]] = []
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        ranks = linear_ranks(fits)
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parents_idx = select_parents_rank(fits, pop_size, rng)
        parent_log.append(parents_idx)
        rank_log.append([ranks[i] for i in parents_idx])
        new_pop = []
        for pi in parents_idx:
            child = build_student(vocab).to(device)
            child.load_state_dict(mutate_state(pop[pi].state_dict(), mutate_scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-RAN",
        "select": "rank",
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "parents_per_gen": parent_log,
        "parent_ranks_per_gen": rank_log,
        "out_path": str(out_path),
    }
