"""H-MUT: H-SEL scaffold; adapt mutate_scale via 1/5 success rule."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from mut_ops import adapt_mutate_scale, fitness_improved
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_mut(
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
    adapt_factor: float = 1.2,
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
        raise RuntimeError("H-MUT: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    scale_hist: list[float] = []
    scale = float(mutate_scale)
    for _gen in range(generations):
        scale_hist.append(scale)
        fits = [_fitness(m, probe) for m in pop]
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        gen_best = fits[ranked[0]]
        history.append(gen_best)
        success = fitness_improved(best_fit, gen_best)
        if success:
            best_fit = gen_best
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        new_pop = []
        for i in range(pop_size):
            child = build_student(vocab).to(device)
            src = parents[i % len(parents)].state_dict()
            child.load_state_dict(mutate_state(src, scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        scale = adapt_mutate_scale(scale, success, factor=adapt_factor)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-MUT",
        "adapt_rule": "one_fifth",
        "adapt_factor": adapt_factor,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "mutate_scale_hist": scale_hist,
        "out_path": str(out_path),
    }
