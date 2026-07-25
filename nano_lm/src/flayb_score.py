"""Score H-FLAYB: dual-budget FCPOOLB path with LAY on non-KV arm."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from cpoolb_score import score_batch_cpoolb
from decode_genes import Gene, clamp_gene
from decode_pool_lay_batch import decode_pool_lay_batch
from eval_student import teacher_mean_logprob
from fcpoolb_score import score_batch_fcpoolb
from flash_ops import gpt_neo_sdpa_context
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from flayb_ops import FLAYB_CHUNK
from kvsel_ops import SMOKE_BUDGETS, should_use_kv
from lay_ops import LayGene, clamp_lay_gene, scale_flops_by_layers
from layer_exit import n_transformer_layers
from load_model import LoadedModel
from student_model import count_params

__all__ = [
    "score_batch_pool_lay",
    "score_batch_flayb",
    "score_batch_fcpoolb",
    "tip_row",
    "FLAYB_CHUNK",
    "SMOKE_BUDGETS",
]


def _policy(gene: Gene) -> Gene:
    g = clamp_gene(dict(gene))
    if "n" in gene:
        g["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        g["temperature"] = float(gene["temperature"])
    if "use_mae" in gene:
        g["use_mae"] = bool(gene["use_mae"])
    return g


def _mean_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    n = max(len(rows), 1)
    keys = (
        "mean_lp",
        "mean_wall_ms",
        "mean_tps",
        "mean_gflops",
        "n_new_total",
        "wall_sum_ms",
    )
    return {k: sum(float(r[k]) for r in rows) / n for k in keys}


def score_batch_pool_lay(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: Gene,
    lay: LayGene | Mapping[str, float | int],
    max_new: int,
    seed: int,
) -> dict[str, float]:
    """Batched BoN+LAY under caller SDPA; layer-scaled GFLOPs."""
    g = _policy(gene)
    lg = clamp_lay_gene(lay)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    n_layers = n_transformer_layers(student)
    results, wall_ms = decode_pool_lay_batch(
        student,
        tok,
        prompts,
        n=int(g["n"]),
        max_new_tokens=max_new,
        temperature=float(g["temperature"]),
        top_p=float(g["top_p"]),
        max_skip=int(lg["max_skip"]),
        lay_conf=float(lg["lay_conf"]),
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
    n = max(len(lps), 1)
    return {
        "mean_lp": sum(lps) / n,
        "mean_wall_ms": float(wall_ms) / n,
        "mean_tps": tokens_per_s(n_new=n_new_total, wall_ms=wall_ms),
        "mean_gflops": sum(gflops) / n,
        "n_new_total": float(n_new_total),
        "wall_sum_ms": float(wall_ms),
    }


def score_batch_flayb(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: Gene,
    lay: LayGene | Mapping[str, float | int],
    seed: int,
    kv_threshold: int,
    chunk_size: int = FLAYB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN POOL tip + LAY tip + KVSEL threshold under SDPA
    WHEN dual budgets (CPOOLB iff KV on; else batched BoN+LAY)
    THEN return mean lp / tok/s / wall / gflops.
    """
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            claim = seed + 1000 * b
            if should_use_kv(b, kv_threshold):
                m = score_batch_cpoolb(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    max_new=b,
                    seed=claim,
                    chunk_size=int(chunk_size),
                )
            else:
                m = score_batch_pool_lay(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    lay=lay,
                    max_new=b,
                    seed=claim,
                )
            rows.append(m)
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out
