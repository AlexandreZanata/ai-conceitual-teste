"""Score serial vs batched EARLY decode (throughput + teacher lp)."""

from __future__ import annotations

from typing import Any, Mapping

from decode_bat import decode_early_batch
from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from load_model import LoadedModel
from student_model import count_params


def _gene(gene: EarlyGene) -> EarlyGene:
    """Clamp exit knobs but keep explicit n/temperature overrides (throughput mode)."""
    e = clamp_early_gene(gene)
    if "n" in gene:
        e["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        e["temperature"] = float(gene["temperature"])
    return e


def score_serial_early(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    max_new: int,
    seed: int,
) -> dict[str, float]:
    e = _gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    lps: list[float] = []
    walls: list[float] = []
    n_new_total = 0
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
        n_new_total += len(result.token_ids)
        ids = tok.encode(text, return_tensors="pt")
        lps.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        flops = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(flops))
    wall_sum = sum(walls)
    n = max(len(lps), 1)
    return {
        "mean_lp": sum(lps) / n,
        "mean_wall_ms": wall_sum / n,
        "mean_tps": tokens_per_s(n_new=n_new_total, wall_ms=wall_sum),
        "mean_gflops": sum(gflops) / n,
        "n_new_total": float(n_new_total),
        "wall_sum_ms": wall_sum,
    }


def score_batch_early(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    max_new: int,
    seed: int,
) -> dict[str, float]:
    e = _gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    results, wall_ms = decode_early_batch(
        student,
        tok,
        prompts,
        n=int(e["n"]),
        max_new_tokens=max_new,
        min_new=int(e["min_new"]),
        conf_threshold=float(e["conf_threshold"]),
        patience=int(e["patience"]),
        temperature=float(e["temperature"]),
        top_p=float(e["top_p"]),
        seed=seed,
        device=device,
    )
    lps: list[float] = []
    gflops: list[float] = []
    n_new_total = 0
    for text, result in zip(prompts, results):
        n_new_total += len(result.token_ids)
        ids = tok.encode(text, return_tensors="pt")
        lps.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        flops = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(flops))
    n = max(len(lps), 1)
    return {
        "mean_lp": sum(lps) / n,
        "mean_wall_ms": float(wall_ms) / n,
        "mean_tps": tokens_per_s(n_new=n_new_total, wall_ms=wall_ms),
        "mean_gflops": sum(gflops) / n,
        "n_new_total": float(n_new_total),
        "wall_sum_ms": float(wall_ms),
    }


def tip_row(
    family: str,
    label: str,
    metrics: Mapping[str, float],
    seed: int,
    gene: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(metrics["mean_lp"]),
        "mean_wall_ms": float(metrics["mean_wall_ms"]),
        "mean_tokens_per_s": float(metrics["mean_tps"]),
        "mean_est_gflops": float(metrics["mean_gflops"]),
        "n_prompts": int(metrics.get("n_prompts", 0)) or None,
        "seed": seed,
        "best_gene": dict(gene),
    }
