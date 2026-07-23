"""H-LOFI: CE-rank full pop; teacher_lp rescore top-k only (vs H-FIT FLOPs)."""

from __future__ import annotations

import copy
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches
from hyp_fit import _prompt_texts, fitness_teacher_lp
from hyp_sel import mutate_state
from load_model import load_causal_lm
from lofi_ops import teacher_forward_budget, top_k_indices, wall_saved
from student_model import build_student, count_params
from train_ce import ce_loss


def _ce_fit(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def run_h_lofi(
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
    top_k: int,
    seq_len: int,
    batch_size: int,
    max_examples: int,
    seed: int,
    out_path: Path,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    prompts = _prompt_texts(prompts_path)
    vocab = len(teacher.tokenizer)
    data = list(
        iter_token_batches(
            teacher.tokenizer,
            cache_dir=cache_dir,
            max_examples=max_examples,
            seq_len=seq_len,
            batch_size=batch_size,
            device=device,
        )
    )
    if not data:
        raise RuntimeError("H-LOFI: no training batches")
    probe = data[0]
    k = min(top_k, pop_size)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    for m in pop:
        m.eval()
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    rescored_log: list[list[int]] = []
    teacher_forwards = 0
    for gen in range(generations):
        ce_scores = [_ce_fit(m, probe) for m in pop]
        top = top_k_indices(ce_scores, k)
        rescored_log.append(top)
        scored: dict[int, float] = {}
        for i in top:
            scored[i] = fitness_teacher_lp(
                pop[i],
                teacher,
                prompts,
                max_new=max_new_fit,
                seed=seed + 1000 * gen + i,
                temperature=temperature,
                top_p=top_p,
            )
            teacher_forwards += len(prompts)
        fits = [scored.get(i, float("-inf")) for i in range(pop_size)]
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_state = copy.deepcopy(pop[ranked[0]].state_dict())
        n_parents = max(1, min(k, pop_size // 2))
        parents = [pop[i] for i in ranked[:n_parents]]
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
    lofi_fw, full_fw = teacher_forward_budget(
        pop_size=pop_size,
        generations=generations,
        n_prompts=len(prompts),
        top_k=k,
    )
    return {
        "hypothesis": "H-LOFI",
        "parents": ["H-FIT"],
        "teacher_rescored_k": k,
        "rescored_per_gen": rescored_log,
        "teacher_forwards": teacher_forwards,
        "teacher_forwards_full_hfit": full_fw,
        "wall_save": wall_saved(teacher_forwards, full_fw),
        "train_wall_s": time.perf_counter() - t0,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "pop_size": pop_size,
        "generations": generations,
        "max_new_fit": max_new_fit,
        "out_path": str(out_path),
        "budget_check_lofi": lofi_fw,
    }
