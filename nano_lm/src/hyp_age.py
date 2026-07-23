"""H-AGE: H-SEL scaffold; ALPS-lite age layers + random immigrants."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from age_ops import bucket_by_layer, child_age, default_age_limits
from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def _breed_layer(
    indices: list[int],
    pop: list[Any],
    ages: list[int],
    fits: list[float],
    vocab: int,
    device: torch.device,
    mutate_scale: float,
) -> tuple[list[Any], list[int]]:
    if not indices:
        return [], []
    ranked = sorted(indices, key=lambda i: fits[i], reverse=True)
    parents = ranked[: max(1, len(ranked) // 2)]
    kids, kid_ages = [], []
    for i in range(len(indices)):
        p = parents[i % len(parents)]
        child = build_student(vocab).to(device)
        child.load_state_dict(mutate_state(pop[p].state_dict(), mutate_scale))
        child.eval()
        kids.append(child)
        kid_ages.append(child_age([ages[p]]))
    return kids, kid_ages


def _inject_immigrants(
    pop: list[Any],
    ages: list[int],
    *,
    n_imm: int,
    pop_size: int,
    vocab: int,
    device: torch.device,
    probe: torch.Tensor,
) -> tuple[list[Any], list[int], int]:
    count = 0
    for _ in range(min(n_imm, pop_size)):
        if not pop:
            break
        worst = min(range(len(pop)), key=lambda i: _fitness(pop[i], probe))
        imm = build_student(vocab).to(device)
        imm.eval()
        pop[worst] = imm
        ages[worst] = 0
        count += 1
    while len(pop) < pop_size:
        m = build_student(vocab).to(device)
        m.eval()
        pop.append(m)
        ages.append(0)
        count += 1
    return pop[:pop_size], ages[:pop_size], count


def _breed_all_layers(
    pop: list[Any],
    ages: list[int],
    fits: list[float],
    limits: list[int],
    vocab: int,
    device: torch.device,
    mutate_scale: float,
) -> tuple[list[Any], list[int]]:
    new_pop: list[Any] = []
    new_ages: list[int] = []
    for layer_idx in bucket_by_layer(ages, limits):
        kids, kid_ages = _breed_layer(
            layer_idx, pop, ages, fits, vocab, device, mutate_scale
        )
        new_pop.extend(kids)
        new_ages.extend(kid_ages)
    return new_pop, new_ages


def run_h_age(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    age_layers: int,
    immigrants_per_gen: int,
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
    limits = default_age_limits(age_layers)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    ages = [0] * pop_size
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
        raise RuntimeError("H-AGE: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    immigrant_hist: list[int] = []
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        top = max(range(pop_size), key=lambda i: fits[i])
        history.append(fits[top])
        if fits[top] > best_fit:
            best_fit = fits[top]
            best_state = copy.deepcopy(pop[top].state_dict())
        new_pop, new_ages = _breed_all_layers(
            pop, ages, fits, limits, vocab, device, mutate_scale
        )
        pop, ages, n_imm = _inject_immigrants(
            new_pop,
            new_ages,
            n_imm=immigrants_per_gen,
            pop_size=pop_size,
            vocab=vocab,
            device=device,
            probe=probe,
        )
        immigrant_hist.append(n_imm)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-AGE",
        "age_layers": age_layers,
        "age_limits": limits,
        "immigrants_per_gen": immigrants_per_gen,
        "immigrant_counts": immigrant_hist,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
