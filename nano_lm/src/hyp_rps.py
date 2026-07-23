"""H-RPS: H-SEL scaffold; rock–paper–scissors niches with cyclic dominance."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from rps_ops import mutate_niche, niche_adjusted_fitness, niche_collapsed
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_rps(
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
    rps_bonus: float = 0.1,
    niche_mut_p: float = 0.2,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    rng = random.Random(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    niches = [i % 3 for i in range(pop_size)]
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
        raise RuntimeError("H-RPS: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    niche_hist: list[list[int]] = []
    collapsed = False
    for _gen in range(generations):
        raws = [_fitness(m, probe) for m in pop]
        fits = niche_adjusted_fitness(raws, niches, bonus=rps_bonus)
        niche_hist.append(list(niches))
        if niche_collapsed(niches):
            collapsed = True
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(raws[ranked[0]])
        if raws[ranked[0]] > best_fit:
            best_fit = raws[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parent_idx = ranked[: max(1, pop_size // 2)]
        new_pop, new_niches = [], []
        for i in range(pop_size):
            src_i = parent_idx[i % len(parent_idx)]
            child = build_student(vocab).to(device)
            child.load_state_dict(mutate_state(pop[src_i].state_dict(), mutate_scale))
            child.eval()
            new_pop.append(child)
            new_niches.append(
                mutate_niche(niches[src_i], rng.random(), p_mut=niche_mut_p)
            )
        pop, niches = new_pop, new_niches
        if device.type == "cuda":
            torch.cuda.empty_cache()
    if niche_collapsed(niches):
        collapsed = True
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-RPS",
        "rps_bonus": rps_bonus,
        "niche_hist": niche_hist,
        "niche_collapsed": collapsed,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
