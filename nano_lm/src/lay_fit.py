"""Score H-LAY genes: teacher lp + wall + layer-scaled GFLOPs."""

from __future__ import annotations

import time
from typing import Any, Mapping

from decode_lay import decode_lay
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from lay_ops import LayGene, clamp_lay_gene, scale_flops_by_layers
from layer_exit import n_transformer_layers
from load_model import LoadedModel
from student_model import count_params


def fitness_lay_detail(
    lay: LayGene,
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, float]:
    """
    GIVEN layer-exit + frozen EARLY tip genes
    WHEN decoding
    THEN return (mean teacher_lp, mean wall_ms, mean est_gflops).
    """
    g = clamp_lay_gene(lay)
    e = clamp_early_gene(early)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    n_layers = n_transformer_layers(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_lay(
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
            max_skip=int(g["max_skip"]),
            lay_conf=float(g["lay_conf"]),
            seed=seed + i,
            device=device,
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        full = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        scaled = scale_flops_by_layers(
            full,
            layer_evals=int(result.layer_evals or 0),
            token_evals=int(result.token_evals),
            n_layers=n_layers,
        )
        gflops.append(to_gflops(scaled))
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
