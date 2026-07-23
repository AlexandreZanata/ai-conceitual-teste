"""H-FIT: H-SEL scaffold; fitness = teacher log-prob on short completions."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch
import yaml

from decode_ar import decode_ar
from eval_student import teacher_mean_logprob
from hyp_sel import mutate_state
from load_model import LoadedModel, load_causal_lm
from student_model import build_student, count_params

FITNESS_KIND = "teacher_lp"


def _prompt_texts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def fitness_teacher_lp(
    student: Any,
    teacher: LoadedModel,
    prompts: list[str],
    *,
    max_new: int,
    seed: int,
    temperature: float,
    top_p: float,
) -> float:
    """Mean teacher log-prob of student AR completions (claim-aligned)."""
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_ar(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=temperature,
            top_p=top_p,
            seed=seed + i,
            device=device,
        )
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores)


def run_h_fit(
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
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    prompts = _prompt_texts(prompts_path)
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
        "hypothesis": "H-FIT",
        "fitness_kind": FITNESS_KIND,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "pop_size": pop_size,
        "generations": generations,
        "max_new_fit": max_new_fit,
        "out_path": str(out_path),
    }
