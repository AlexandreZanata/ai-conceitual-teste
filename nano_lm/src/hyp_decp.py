"""H-DECP: per-prompt gene bank; claim picks by student proxy."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import yaml

from dec_fit_ops import fitness_gene_detail
from decp_search import claim_with_bank, evolve_gene
from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_decp(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    pop_size: int,
    generations: int,
    max_new: int,
    seed: int,
    out_meta: Path,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    fit_prompts = _prompts(prompts_path)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    t0 = time.perf_counter()
    bank = []
    bank_fits: list[float] = []
    for i, text in enumerate(fit_prompts):
        gene, fit = evolve_gene(
            teacher=teacher,
            student=student,
            prompts=[text],
            pop_size=pop_size,
            generations=generations,
            max_new=max_new,
            seed=seed + 17 * (i + 1),
        )
        bank.append(gene)
        bank_fits.append(fit)
    global_gene, global_fit = evolve_gene(
        teacher=teacher,
        student=student,
        prompts=fit_prompts,
        pop_size=pop_size,
        generations=generations,
        max_new=max_new,
        seed=seed + 999,
    )
    eval_lp, eval_wall, picks = claim_with_bank(
        bank,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    glo_lp, glo_wall = fitness_gene_detail(
        global_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 8888,
    )
    meta = {
        "hypothesis": "H-DECP",
        "bank": bank,
        "bank_fits": bank_fits,
        "global_gene": global_gene,
        "global_fit": global_fit,
        "best_fit": float(sum(bank_fits) / len(bank_fits)),
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "global_eval_fit": glo_lp,
        "global_eval_wall_ms": glo_wall,
        "picks": picks,
        "eval_max_new": hold,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
