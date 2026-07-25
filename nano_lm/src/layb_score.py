"""Score H-LAYB: dual-budget FUSEB path with LAY on non-KV arm."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from cbat_score import score_batch_cbat
from decode_lay_batch import decode_lay_batch
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flash_ops import gpt_neo_sdpa_context
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from fuseb_score import score_batch_fuseb
from kvsel_ops import SMOKE_BUDGETS, should_use_kv
from lay_ops import LayGene, clamp_lay_gene, scale_flops_by_layers
from layb_ops import LAYB_CHUNK
from layer_exit import n_transformer_layers
from load_model import LoadedModel
from student_model import count_params

__all__ = [
    "score_batch_lay",
    "score_batch_layb",
    "score_batch_fuseb",
    "tip_row",
    "LAYB_CHUNK",
    "SMOKE_BUDGETS",
]


def _gene(gene: EarlyGene) -> EarlyGene:
    e = clamp_early_gene(gene)
    if "n" in gene:
        e["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        e["temperature"] = float(gene["temperature"])
    return e


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


def score_batch_lay(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    lay: LayGene | Mapping[str, float | int],
    max_new: int,
    seed: int,
) -> dict[str, float]:
    """Batched LAY decode under caller SDPA; layer-scaled GFLOPs."""
    e = _gene(gene)
    g = clamp_lay_gene(lay)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    n_layers = n_transformer_layers(student)
    results, wall_ms = decode_lay_batch(
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
        max_skip=int(g["max_skip"]),
        lay_conf=float(g["lay_conf"]),
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


def score_batch_layb(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    lay: LayGene | Mapping[str, float | int],
    seed: int,
    kv_threshold: int,
    chunk_size: int = LAYB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN EARLY tip + LAY tip + KVSEL threshold under SDPA
    WHEN dual budgets (CHBAT iff KV on; else batched LAY)
    THEN return mean lp / tok/s / wall / gflops.
    """
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            claim = seed + 1000 * b
            if should_use_kv(b, kv_threshold):
                m = score_batch_cbat(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    max_new=b,
                    seed=claim,
                    chunk_size=int(chunk_size),
                )
            else:
                m = score_batch_lay(
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
