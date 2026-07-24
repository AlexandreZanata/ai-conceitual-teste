"""Score serial vs batched POOL/BoN decode (throughput + teacher lp)."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from decode_genes import Gene, clamp_gene
from decode_poolb import decode_bon_batch
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from load_model import LoadedModel
from student_model import count_params

__all__ = ["throughput_gene", "score_serial_pool", "score_batch_pool", "tip_row"]


def throughput_gene(tip: Mapping[str, Any]) -> Gene:
    """
    GIVEN frozen POOL tip
    WHEN building throughput claim policy
    THEN keep tip top_p; force n=1 near-greedy BoN (lp fidelity vs batch seed).
    """
    g = clamp_gene(dict(tip))
    g["n"] = 1
    g["temperature"] = 1e-6
    g["use_mae"] = False
    return g


def _policy(gene: Gene) -> Gene:
    """Clamp POOL knobs then re-apply throughput overrides (temp may be < BOUNDS)."""
    g = clamp_gene(dict(gene))
    if "n" in gene:
        g["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        g["temperature"] = float(gene["temperature"])
    if "use_mae" in gene:
        g["use_mae"] = bool(gene["use_mae"])
    return g


def score_serial_pool(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: Gene,
    max_new: int,
    seed: int,
) -> dict[str, float]:
    """Serial = one-prompt batches (same kernel as multi-prompt; fair lp/tok/s)."""
    g = _policy(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    lps: list[float] = []
    walls: list[float] = []
    n_new_total = 0
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        results, wall_ms = decode_bon_batch(
            student,
            tok,
            [text],
            n=int(g["n"]),
            max_new_tokens=max_new,
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            seed=seed + i,
            device=device,
        )
        result = results[0]
        walls.append(float(wall_ms))
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


def score_batch_pool(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: Gene,
    max_new: int,
    seed: int,
) -> dict[str, float]:
    g = _policy(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    results, wall_ms = decode_bon_batch(
        student,
        tok,
        prompts,
        n=int(g["n"]),
        max_new_tokens=max_new,
        temperature=float(g["temperature"]),
        top_p=float(g["top_p"]),
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
