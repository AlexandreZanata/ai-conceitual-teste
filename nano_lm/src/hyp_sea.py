"""H-SEA: H-FIT scaffold; odd gens CE-fit, even gens teacher_lp-fit."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches
from hyp_fit import _prompt_texts, fitness_teacher_lp
from hyp_sel import mutate_state
from load_model import load_causal_lm
from sea_ops import season_kind
from student_model import build_student, count_params
from train_ce import ce_loss


def _ce_fit(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_sea(
    *,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    mutate_scale: float,
    max_new_fit: int,
    seq_len: int,
    batch_size: int,
    max_examples: int,
    seed: int,
    out_path: Path,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    prompts = _prompt_texts(prompts_path)
    vocab = len(teacher.tokenizer)
    tok = teacher.tokenizer
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
        raise RuntimeError("H-SEA: no training batches")
    probe = data[0]
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    for m in pop:
        m.eval()
    best_state = None
    best_lp = float("-inf")
    history: list[float] = []
    season_log: list[str] = []
    for gen in range(generations):
        kind = season_kind(gen)
        season_log.append(kind)
        if kind == "ce":
            fits = [_ce_fit(m, probe) for m in pop]
        else:
            fits = [
                fitness_teacher_lp(
                    m,
                    teacher,
                    prompts,
                    max_new=max_new_fit,
                    seed=seed + 1000 * gen + i,
                    temperature=temperature,
                    top_p=top_p,
                )
                for i, m in enumerate(pop)
            ]
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if kind == "teacher_lp" and fits[ranked[0]] > best_lp:
            best_lp = fits[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        new_pop = []
        for i in range(pop_size):
            child = build_student(vocab).to(device)
            src = parents[i % len(parents)].state_dict()
            child.load_state_dict(mutate_state(src, mutate_scale))
            child.eval()
            new_pop.append(child)
        pop = new_pop
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-SEA",
        "fitness_kind": "seasonal_ce_teacher_lp",
        "season_log": season_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_lp,
        "history": history,
        "out_path": str(out_path),
    }
