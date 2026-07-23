"""H-NIC: H-SEL scaffold; fitness sharing by mean L2 in weight space."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from nic_ops import share_fitness
from student_model import build_student, count_params
from train_ce import ce_loss
from xov_ops import pop_diversity


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_nic(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    niche_alpha: float,
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
        raise RuntimeError("H-NIC: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    div_hist: list[float] = []
    for _gen in range(generations):
        raw = [_fitness(m, probe) for m in pop]
        states = [copy.deepcopy(m.state_dict()) for m in pop]
        div_hist.append(pop_diversity(states))
        shared = share_fitness(raw, states, niche_alpha)
        ranked = sorted(range(pop_size), key=lambda i: shared[i], reverse=True)
        history.append(shared[ranked[0]])
        if raw[ranked[0]] > best_fit:
            best_fit = raw[ranked[0]]
            best_state = states[ranked[0]]
        parents = [states[i] for i in ranked[: max(1, pop_size // 2)]]
        new_pop = []
        for i in range(pop_size):
            child = build_student(vocab).to(device)
            child.load_state_dict(mutate_state(parents[i % len(parents)], mutate_scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    div_up = bool(div_hist) and div_hist[-1] > div_hist[0] + 1e-9
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-NIC",
        "niche_alpha": niche_alpha,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "diversity": div_hist,
        "diversity_up": div_up,
        "out_path": str(out_path),
    }
