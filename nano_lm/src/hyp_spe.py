"""H-SPE: H-SEL scaffold; multi-island breed + ring migrate top-1."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from spe_ops import (
    best_in_island,
    ring_migrate_pairs,
    should_migrate,
    split_islands,
    worst_in_island,
)
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def _breed_island(
    indices: list[int],
    pop: list[Any],
    fits: list[float],
    vocab: int,
    device: torch.device,
    mutate_scale: float,
) -> list[Any]:
    ranked = sorted(indices, key=lambda i: fits[i], reverse=True)
    parents = [pop[i] for i in ranked[: max(1, len(ranked) // 2)]]
    kids = []
    for i in range(len(indices)):
        child = build_student(vocab).to(device)
        src = parents[i % len(parents)].state_dict()
        child.load_state_dict(mutate_state(src, mutate_scale))
        child.eval()
        kids.append(child)
    return kids


def _apply_migration(
    pop: list[Any],
    fits: list[float],
    islands: list[list[int]],
) -> list[dict[str, int]]:
    log: list[dict[str, int]] = []
    for src, dst in ring_migrate_pairs(len(islands)):
        donor = best_in_island(fits, islands[src])
        victim = worst_in_island(fits, islands[dst])
        pop[victim].load_state_dict(copy.deepcopy(pop[donor].state_dict()))
        pop[victim].eval()
        log.append({"src_island": src, "dst_island": dst, "donor": donor, "victim": victim})
    return log


def run_h_spe(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    n_islands: int,
    migrate_every: int,
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
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
    islands = split_islands(pop_size, n_islands)
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
        raise RuntimeError("H-SPE: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    migration_log: list[dict[str, Any]] = []
    for gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        top = max(range(pop_size), key=lambda i: fits[i])
        history.append(fits[top])
        if fits[top] > best_fit:
            best_fit = fits[top]
            best_state = copy.deepcopy(pop[top].state_dict())
        if should_migrate(gen, migrate_every):
            migration_log.append(
                {"gen": gen, "moves": _apply_migration(pop, fits, islands)}
            )
        new_pop: list[Any] = [None] * pop_size  # type: ignore[list-item]
        for isle in islands:
            kids = _breed_island(isle, pop, fits, vocab, device, mutate_scale)
            for slot, child in zip(isle, kids):
                new_pop[slot] = child
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-SPE",
        "n_islands": n_islands,
        "migrate_every": migrate_every,
        "island_indices": islands,
        "migration_log": migration_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
