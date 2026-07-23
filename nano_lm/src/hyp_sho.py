"""H-SHO: H-SEL scaffold; after mutate, reinit one random child layer."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from sho_ops import layer_prefixes, pick_prefix, shock_state
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_sho(
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
        raise RuntimeError("H-SHO: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    shock_log: list[list[str]] = []
    prefixes = layer_prefixes(list(pop[0].state_dict().keys()))
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        fresh = build_student(vocab).state_dict()
        new_pop = []
        gen_shocks: list[str] = []
        for i in range(pop_size):
            child = build_student(vocab).to(device)
            src = parents[i % len(parents)].state_dict()
            mutated = mutate_state(src, mutate_scale)
            prefix = pick_prefix(prefixes, rng.randrange(len(prefixes)))
            child.load_state_dict(shock_state(mutated, fresh, prefix))
            child.eval()
            new_pop.append(child)
            gen_shocks.append(prefix)
        pop = new_pop
        shock_log.append(gen_shocks)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-SHO",
        "layer_prefixes": prefixes,
        "shocks_per_gen": shock_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
