"""Score H-SHORT genes: teacher lp + wall + est GFLOPs."""

from __future__ import annotations

from typing import Any, Mapping

from decode_early import decode_early
from decode_short import decode_short
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from short_ops import ShortGene, clamp_short_gene
from student_model import count_params


def fitness_short_detail(
    short: ShortGene,
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, float]:
    """
    GIVEN short-draft + frozen EARLY tip genes
    WHEN decoding
    THEN return (mean teacher_lp, mean wall_ms, mean est_gflops).
    """
    e = clamp_early_gene(early)
    g = clamp_short_gene(short, e)
    draft_max = min(int(g["draft_max"]), int(max_new))
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_short(
            student,
            tok,
            text,
            n=int(e["n"]),
            max_new_tokens=max_new,
            draft_max=draft_max,
            stop_conf=float(g["stop_conf"]),
            min_new=int(e["min_new"]),
            conf_threshold=float(e["conf_threshold"]),
            patience=int(e["patience"]),
            temperature=float(e["temperature"]),
            top_p=float(e["top_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        flops = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(flops))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def fitness_early_detail(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, float]:
    e = clamp_early_gene(early)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_early(
            student,
            tok,
            text,
            n=int(e["n"]),
            max_new_tokens=max_new,
            min_new=int(e["min_new"]),
            conf_threshold=float(e["conf_threshold"]),
            patience=int(e["patience"]),
            temperature=float(e["temperature"]),
            top_p=float(e["top_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        flops = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(flops))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def tip_row(
    family: str,
    label: str,
    lp: float,
    wall: float,
    gf: float,
    seed: int,
    gene: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "mean_est_gflops": float(gf),
        "n_prompts": 2,
        "seed": seed,
        "best_gene": dict(gene),
    }
