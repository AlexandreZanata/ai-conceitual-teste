"""H-SEL: population of students; fitness = teacher NLL; mutate winners."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from student_model import build_student, count_params
from train_ce import ce_loss


def _mutate(state: dict[str, torch.Tensor], scale: float) -> dict[str, torch.Tensor]:
    out = {}
    for k, v in state.items():
        if v.dtype.is_floating_point:
            out[k] = v + scale * torch.randn_like(v)
        else:
            out[k] = v.clone()
    return out


def run_h_sel(
    *,
    teacher_id: str,
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
    tok = load_tokenizer(tokenizer_id, cache_dir)
    pop = [build_student(len(tok)).to(device) for _ in range(pop_size)]
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
        raise RuntimeError("H-SEL: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    for _gen in range(generations):
        fits: list[float] = []
        for m in pop:
            with torch.no_grad():
                loss = ce_loss(m(probe).logits, probe)
                fit = -float(loss.item())
            fits.append(fit)
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        new_pop = []
        for i in range(pop_size):
            child = build_student(len(tok)).to(device)
            src = parents[i % len(parents)].state_dict()
            child.load_state_dict(_mutate(src, mutate_scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-SEL",
        "params": count_params(pop[0]),
        "best_fit": best_fit,
        "history": history,
        "out_path": str(out_path),
    }
