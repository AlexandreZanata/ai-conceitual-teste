"""H-HOLD: H-FIT scaffold; select on fit prompts; claim eval must be disjoint."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from hold_ops import assert_disjoint, load_prompt_ids
from hyp_fit import FITNESS_KIND, _prompt_texts, fitness_teacher_lp
from hyp_sel import mutate_state
from load_model import load_causal_lm
from student_model import build_student, count_params


def run_h_hold(
    *,
    teacher_id: str,
    tokenizer_id: str,
    fit_prompts_path: Path,
    eval_prompts_path: Path,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    mutate_scale: float,
    max_new_fit: int,
    seed: int,
    out_path: Path,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    fit_ids = load_prompt_ids(fit_prompts_path)
    eval_ids = load_prompt_ids(eval_prompts_path)
    assert_disjoint(fit_ids, eval_ids)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    prompts = _prompt_texts(fit_prompts_path)
    vocab = len(teacher.tokenizer)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    for m in pop:
        m.eval()
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    for gen in range(generations):
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
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
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
        "hypothesis": "H-HOLD",
        "fitness_kind": FITNESS_KIND,
        "fit_prompt_ids": fit_ids,
        "eval_prompt_ids": eval_ids,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "pop_size": pop_size,
        "generations": generations,
        "max_new_fit": max_new_fit,
        "out_path": str(out_path),
    }
