"""H-XOV: H-SEL scaffold; uniform weight crossover then mutate."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from elite_ops import diversity_collapsed
from hyp_sel import mutate_state
from student_model import build_student, count_params
from train_ce import ce_loss
from xov_ops import blend_state_dicts, pick_parent_pair, pop_diversity


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_xov(
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
        raise RuntimeError("H-XOV: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    div_hist: list[float] = []
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        states = [copy.deepcopy(m.state_dict()) for m in pop]
        div_hist.append(pop_diversity(states))
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_state = states[ranked[0]]
        parents = [states[i] for i in ranked[: max(1, pop_size // 2)]]
        new_pop = []
        for _ in range(pop_size):
            i, j = pick_parent_pair(len(parents), rng)
            blended = blend_state_dicts(parents[i], parents[j], rng)
            child = build_student(vocab).to(device)
            child.load_state_dict(mutate_state(blended, mutate_scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    collapsed = diversity_collapsed(div_hist[0], div_hist[-1]) if div_hist else True
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-XOV",
        "crossover": 1,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "diversity": div_hist,
        "diversity_collapsed": collapsed,
        "out_path": str(out_path),
    }
