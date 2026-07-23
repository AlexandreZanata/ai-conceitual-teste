"""H-HIB: H-SEL scaffold; periodic hibernation inherits parent fit × decay."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hib_ops import inherit_fits, should_hibernate
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
) -> tuple[list[Any], list[float]]:
    n = len(pop)
    ranked = sorted(range(n), key=lambda i: fits[i], reverse=True)
    parent_idx = ranked[: max(1, n // 2)]
    new_pop: list[Any] = []
    inherited: list[float] = []
    for i in range(n):
        src_i = parent_idx[i % len(parent_idx)]
        child = build_student(vocab).to(device)
        child.load_state_dict(mutate_state(pop[src_i].state_dict(), mutate_scale))
        child.eval()
        new_pop.append(child)
        inherited.append(fits[src_i])
    return new_pop, inherited


def run_h_hib(
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
    hib_every: int = 2,
    decay: float = 0.9,
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
        raise RuntimeError("H-HIB: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    hib_log: list[dict[str, int | bool]] = []
    inherited: list[float] = [0.0] * pop_size
    for gen in range(generations):
        hib = should_hibernate(gen, hib_every)
        if hib:
            fits = inherit_fits(inherited, decay)
            skipped = pop_size
        else:
            fits = [_fitness(m, probe) for m in pop]
            skipped = 0
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        top = ranked[0]
        true_top = _fitness(pop[top], probe) if hib else fits[top]
        history.append(true_top)
        hib_log.append({"gen": gen, "hibernated": hib, "skipped_evals": skipped})
        if true_top > best_fit:
            best_fit = true_top
            best_state = copy.deepcopy(pop[top].state_dict())
        pop, inherited = _breed(
            pop, fits, vocab=vocab, device=device, mutate_scale=mutate_scale
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-HIB",
        "hib_every": hib_every,
        "decay": decay,
        "hibernate_log": hib_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
