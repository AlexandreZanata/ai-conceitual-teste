"""H-QG: hard quality gate then minimize est. GFLOPs on EARLY genes."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from earf_fit import fitness_earf_detail
from early_ops import clamp_early_gene, mutate_early_gene
from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json
from qg_ops import passes_quality_gate, pick_min_gflops, seed_qg_from_tip


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _init_pop(rng: random.Random, tip: dict[str, Any], pop_size: int) -> list[dict]:
    pop = [clamp_early_gene(tip)]
    while len(pop) < pop_size:
        pop.append(seed_qg_from_tip(tip, rng))
    return pop


def _eligible(lps: list[float], tip_lp: float) -> list[int]:
    out = [i for i, lp in enumerate(lps) if passes_quality_gate(lp, tip_lp)]
    if 0 not in out:
        out.append(0)  # tip slot always survives noise
    return out


def run_h_qg(
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
    tip_gene: dict[str, Any],
    out_meta: Path,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    fit_prompts = _prompts(prompts_path)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    tip = clamp_early_gene(tip_gene)
    tip_lp, _tw, tip_gf = fitness_earf_detail(
        tip,
        teacher=teacher,
        student=student,
        prompts=fit_prompts,
        max_new=max_new,
        seed=seed + 42,
    )
    pop = _init_pop(rng, tip, pop_size)
    history: list[dict[str, Any]] = []
    best_gene, best_lp, best_gf = tip, tip_lp, tip_gf
    empty_gens = 0
    t0 = time.perf_counter()
    for gen in range(generations):
        pop[0] = tip
        details = [
            fitness_earf_detail(
                g,
                teacher=teacher,
                student=student,
                prompts=fit_prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
            )
            for g in pop
        ]
        lps = [d[0] for d in details]
        gfs = [d[2] for d in details]
        raw = pick_min_gflops(lps, gfs, tip_lp)
        if raw is None:
            empty_gens += 1
        elig = _eligible(lps, tip_lp)
        pick = min(elig, key=lambda i: float(gfs[i]))
        history.append(
            {"gen": gen, "pick_gflops": gfs[pick], "n_eligible": len(elig)}
        )
        if gfs[pick] < best_gf - 1e-12 or (
            abs(gfs[pick] - best_gf) <= 1e-12 and lps[pick] > best_lp
        ):
            best_gf, best_lp = gfs[pick], lps[pick]
            best_gene = clamp_early_gene(pop[pick])
        parents = [pop[i] for i in sorted(elig, key=lambda i: gfs[i])]
        pop = [tip] + [
            mutate_early_gene(parents[i % len(parents)], rng)
            for i in range(pop_size - 1)
        ]
    eval_lp, eval_wall, eval_gf = fitness_earf_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-QG",
        "tip_lp_floor": tip_lp,
        "best_gene": best_gene,
        "best_fit": best_lp,
        "best_gflops": best_gf,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_est_gflops": eval_gf,
        "empty_gens": empty_gens,
        "empty_rate": float(empty_gens) / max(generations, 1),
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
