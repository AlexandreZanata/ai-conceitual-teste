"""H-JOINT: bank curriculum ckpts; evolve joint early+curriculum gene."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from early_fit import fitness_early_detail
from eval_student import load_student_ckpt
from hyp_cur import run_h_cur
from joint_ops import (
    JOINT_LOS,
    JOINT_STAGES,
    clamp_joint_gene,
    mutate_joint_gene,
    random_joint_gene,
)
from lat2_ops import MIN_LAM
from lat_ops import latency_aware_score
from load_model import load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _bank_key(seq_lo: int, n_stages: int) -> str:
    return f"lo{int(seq_lo)}_n{int(n_stages)}"


def _build_bank(
    *,
    c: dict[str, Any],
    device: torch.device,
    seed: int,
    out_dir: Path,
) -> dict[str, Path]:
    bank: dict[str, Path] = {}
    steps = int(c.get("steps_cur", c["steps_kd"]))
    for seq_lo in JOINT_LOS:
        for n_stages in JOINT_STAGES:
            key = _bank_key(seq_lo, n_stages)
            path = out_dir / f"HJOINT_{key}_seed{seed}.pt"
            tip = out_dir / f"HCURL_lo{seq_lo}_seed{seed}.pt"
            if int(n_stages) == 3 and tip.is_file():
                bank[key] = tip
                continue
            if not path.is_file():
                run_h_cur(
                    teacher_id=c["teacher_id"],
                    tokenizer_id=c["tokenizer_id"],
                    cache_dir=c["cache"],
                    device=device,
                    steps=steps,
                    batch_size=c["batch_size"],
                    seq_len=c["seq_len"],
                    max_examples=c["max_examples"],
                    lr=c["lr"],
                    seed=seed + 11 * seq_lo + n_stages,
                    temperature=2.0,
                    alpha=0.5,
                    out_path=path,
                    seq_lo=int(seq_lo),
                    n_stages=int(n_stages),
                )
            bank[key] = path
            if device.type == "cuda":
                torch.cuda.empty_cache()
    return bank


def _score_pop(
    pop: list,
    *,
    bank: dict[str, Path],
    teacher: Any,
    fit_prompts: list[str],
    max_new: int,
    seed: int,
    gen: int,
    lam: float,
) -> tuple[list[tuple[float, float]], list[float]]:
    details: list[tuple[float, float]] = []
    scores: list[float] = []
    for g in pop:
        ckpt = bank[_bank_key(int(g["seq_lo"]), int(g["n_stages"]))]
        student = load_student_ckpt(ckpt, teacher.tokenizer, teacher.device)
        lp, wall = fitness_early_detail(
            g,
            teacher=teacher,
            student=student,
            prompts=fit_prompts,
            max_new=max_new,
            seed=seed + 1000 * gen,
        )
        details.append((lp, wall))
        scores.append(latency_aware_score(lp, wall, lam))
    return details, scores


def run_h_joint(
    *,
    c: dict[str, Any],
    device: torch.device,
    seed: int,
    out_dir: Path,
    pop_size: int,
    generations: int,
    max_new: int,
    eval_max_new: int,
    lam: float = MIN_LAM,
) -> dict[str, Any]:
    rng = random.Random(seed)
    bank = _build_bank(c=c, device=device, seed=seed, out_dir=out_dir)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    fit_prompts = _prompts(c["prompts"])
    pop = [random_joint_gene(rng) for _ in range(pop_size)]
    best_gene = pop[0]
    best_score = float("-inf")
    best_lp = float("-inf")
    history: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for gen in range(generations):
        details, scores = _score_pop(
            pop,
            bank=bank,
            teacher=teacher,
            fit_prompts=fit_prompts,
            max_new=max_new,
            seed=seed,
            gen=gen,
            lam=lam,
        )
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_score": scores[ranked[0]],
                "best_seq_lo": pop[ranked[0]]["seq_lo"],
                "best_n_stages": pop[ranked[0]]["n_stages"],
            }
        )
        if scores[ranked[0]] > best_score:
            best_score = scores[ranked[0]]
            best_lp = details[ranked[0]][0]
            best_gene = clamp_joint_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_joint_gene(parents[i % len(parents)], rng)
            for i in range(pop_size)
        ]
    claim_ckpt = bank[
        _bank_key(int(best_gene["seq_lo"]), int(best_gene["n_stages"]))
    ]
    student = load_student_ckpt(claim_ckpt, teacher.tokenizer, teacher.device)
    eval_lp, eval_wall = fitness_early_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=fit_prompts,
        max_new=eval_max_new,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-JOINT",
        "lam": lam,
        "best_gene": best_gene,
        "best_score": best_score,
        "best_fit": best_lp,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "ckpt": str(claim_ckpt),
    }
    write_json(out_dir / f"HJOINT_seed{seed}_train.json", meta)
    return meta
