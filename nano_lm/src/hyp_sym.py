"""H-SYM: H-SEL scaffold; obligate pairs — both must beat mean to breed."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from student_model import build_student, count_params
from sym_ops import eligible_above_mean, obligate_pairs
from train_ce import ce_loss
from xov_ops import blend_state_dicts


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_sym(
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
        raise RuntimeError("H-SYM: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    pairs_log: list[list[list[int]]] = []
    sterile_gens = 0
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        top = max(range(pop_size), key=lambda i: fits[i])
        history.append(fits[top])
        if fits[top] > best_fit:
            best_fit = fits[top]
            best_state = copy.deepcopy(pop[top].state_dict())
        eligible = eligible_above_mean(fits)
        pairs = obligate_pairs(eligible)
        pairs_log.append([list(p) for p in pairs])
        new_pop: list[Any] = []
        if not pairs:
            sterile_gens += 1
            src = pop[top].state_dict()
            for _ in range(pop_size):
                child = build_student(vocab).to(device)
                child.load_state_dict(mutate_state(src, mutate_scale))
                child.eval()
                new_pop.append(child)
        else:
            for i in range(pop_size):
                a, b = pairs[i % len(pairs)]
                blended = blend_state_dicts(
                    pop[a].state_dict(), pop[b].state_dict(), rng
                )
                child = build_student(vocab).to(device)
                child.load_state_dict(mutate_state(blended, mutate_scale))
                child.eval()
                new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-SYM",
        "obligate": "both_above_mean",
        "mean_fit_rule": True,
        "pairs_per_gen": pairs_log,
        "sterile_gens": sterile_gens,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
