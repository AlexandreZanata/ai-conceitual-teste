"""H-FXS: H-FIT fitness + H-XOV crossover + H-SHO layer shock."""

from __future__ import annotations

import copy
import random
from pathlib import Path
from typing import Any

import torch

from fxs_ops import PARENTS, breed_fxs_state
from hyp_fit import FITNESS_KIND, _prompt_texts, fitness_teacher_lp
from load_model import load_causal_lm
from sho_ops import layer_prefixes
from student_model import build_student, count_params
from xov_ops import pick_parent_pair


def run_h_fxs(
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
    seed: int,
    out_path: Path,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    prompts = _prompt_texts(prompts_path)
    vocab = len(teacher.tokenizer)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    for m in pop:
        m.eval()
    prefixes = layer_prefixes(list(pop[0].state_dict().keys()))
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    shock_log: list[list[str]] = []
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
        parents = [pop[i].state_dict() for i in ranked[: max(1, pop_size // 2)]]
        fresh = build_student(vocab).state_dict()
        new_pop = []
        gen_shocks: list[str] = []
        for _ in range(pop_size):
            i, j = pick_parent_pair(len(parents), rng)
            child = build_student(vocab).to(device)
            state, prefix = breed_fxs_state(
                parents[i], parents[j], fresh, prefixes, rng, mutate_scale
            )
            child.load_state_dict(state)
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
        "hypothesis": "H-FXS",
        "parents": list(PARENTS),
        "fitness_kind": FITNESS_KIND,
        "crossover": 1,
        "layer_prefixes": prefixes,
        "shocks_per_gen": shock_log,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "pop_size": pop_size,
        "generations": generations,
        "max_new_fit": max_new_fit,
        "out_path": str(out_path),
    }
