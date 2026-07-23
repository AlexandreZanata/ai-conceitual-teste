"""H-GLD: H-FIT scaffold; select by Goldilocks mid-band teacher_lp score."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from gld_ops import goldilocks_scores
from hyp_fit import _prompt_texts, fitness_teacher_lp
from hyp_sel import mutate_state
from load_model import load_causal_lm
from student_model import build_student, count_params


def run_h_gld(
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
    gld_mid: float = -17.0,
    gld_width: float = 2.0,
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
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    for m in pop:
        m.eval()
    best_state = None
    best_raw = float("-inf")
    history: list[float] = []
    gld_hist: list[list[float]] = []
    for gen in range(generations):
        raws = [
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
        glds = goldilocks_scores(raws, mid=gld_mid, width=gld_width)
        gld_hist.append(glds)
        ranked = sorted(range(pop_size), key=lambda i: glds[i], reverse=True)
        top_raw = max(raws)
        history.append(top_raw)
        if top_raw > best_raw:
            best_raw = top_raw
            best_i = max(range(pop_size), key=lambda i: raws[i])
            best_state = copy.deepcopy(pop[best_i].state_dict())
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
        "hypothesis": "H-GLD",
        "fitness_kind": "goldilocks_teacher_lp",
        "gld_mid": gld_mid,
        "gld_width": gld_width,
        "gld_scores_per_gen": gld_hist,
        "params": count_params(build_student(vocab)),
        "best_fit": best_raw,
        "history": history,
        "out_path": str(out_path),
    }
