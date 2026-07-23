"""H-CAT: H-SEL scaffold; periodic catastrophe keeps top-1 + immigrants."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from cat_ops import elite_index, immigrant_count, should_catastrophe
from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def _breed(
    pop: list[Any],
    fits: list[float],
    *,
    vocab: int,
    device: torch.device,
    mutate_scale: float,
) -> list[Any]:
    n = len(pop)
    ranked = sorted(range(n), key=lambda i: fits[i], reverse=True)
    parents = [pop[i] for i in ranked[: max(1, n // 2)]]
    new_pop = []
    for i in range(n):
        child = build_student(vocab).to(device)
        src = parents[i % len(parents)].state_dict()
        child.load_state_dict(mutate_state(src, mutate_scale))
        child.eval()
        new_pop.append(child)
    return new_pop


def _catastrophe(
    pop: list[Any],
    fits: list[float],
    *,
    vocab: int,
    device: torch.device,
) -> tuple[list[Any], int]:
    n = len(pop)
    elite = elite_index(fits)
    survivor = build_student(vocab).to(device)
    survivor.load_state_dict(copy.deepcopy(pop[elite].state_dict()))
    survivor.eval()
    n_imm = immigrant_count(n, keep=1)
    new_pop = [survivor]
    for _ in range(n_imm):
        imm = build_student(vocab).to(device)
        imm.eval()
        new_pop.append(imm)
    return new_pop, n_imm


def run_h_cat(
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
    cat_every: int = 2,
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
        raise RuntimeError("H-CAT: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    cat_log: list[dict[str, int]] = []
    for gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        top = elite_index(fits)
        history.append(fits[top])
        if fits[top] > best_fit:
            best_fit = fits[top]
            best_state = copy.deepcopy(pop[top].state_dict())
        if should_catastrophe(gen, cat_every):
            pop, n_imm = _catastrophe(pop, fits, vocab=vocab, device=device)
            cat_log.append({"gen": gen, "immigrants": n_imm})
        else:
            pop = _breed(
                pop, fits, vocab=vocab, device=device, mutate_scale=mutate_scale
            )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-CAT",
        "cat_every": cat_every,
        "catastrophe_log": cat_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
