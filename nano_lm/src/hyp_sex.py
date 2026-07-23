"""H-SEX: H-SEL scaffold; mate choice by fitness × pairwise L2, then crossover."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from sex_ops import choose_mate, pairwise_l2
from student_model import build_student, count_params
from train_ce import ce_loss
from xov_ops import blend_state_dicts


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def _breed_generation(
    pop: list[Any],
    fits: list[float],
    states: list[dict[str, torch.Tensor]],
    vocab: int,
    device: torch.device,
    mutate_scale: float,
    rng: random.Random,
) -> tuple[list[Any], list[list[int]]]:
    pop_size = len(pop)
    ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
    parent_idx = ranked[: max(1, pop_size // 2)]
    p_states = [states[i] for i in parent_idx]
    p_fits = [fits[i] for i in parent_idx]
    dist = pairwise_l2(p_states)
    cand = list(range(len(parent_idx)))
    pairs: list[list[int]] = []
    kids: list[Any] = []
    for c in range(pop_size):
        i = c % len(parent_idx)
        j = choose_mate(i, cand, p_fits, dist[i])
        pairs.append([parent_idx[i], parent_idx[j]])
        blended = blend_state_dicts(p_states[i], p_states[j], rng)
        child = build_student(vocab).to(device)
        child.load_state_dict(mutate_state(blended, mutate_scale))
        child.eval()
        kids.append(child)
    return kids, pairs


def run_h_sex(
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
        raise RuntimeError("H-SEX: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    pairs_log: list[list[list[int]]] = []
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        states = [copy.deepcopy(m.state_dict()) for m in pop]
        top = max(range(pop_size), key=lambda i: fits[i])
        history.append(fits[top])
        if fits[top] > best_fit:
            best_fit = fits[top]
            best_state = states[top]
        pop, pairs = _breed_generation(
            pop, fits, states, vocab, device, mutate_scale, rng
        )
        pairs_log.append(pairs)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-SEX",
        "mate_choice": "fit_x_l2",
        "pairs_per_gen": pairs_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
