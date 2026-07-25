"""Score H-GALLF: always CUDA-graph BoN+LAY arm (no KV/CPOOLB) under SDPA."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from decode_genes import Gene
from flash_ops import gpt_neo_sdpa_context
from gallf_ops import GALLF_CHUNK
from graphf_score import SMOKE_BUDGETS, score_batch_graphf, score_batch_graphf_arm
from lay_ops import LayGene

__all__ = [
    "score_batch_gallf",
    "score_batch_graphf",
    "tip_row",
    "GALLF_CHUNK",
    "SMOKE_BUDGETS",
]


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


def score_batch_gallf(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: Gene,
    lay: LayGene | Mapping[str, float | int],
    seed: int,
    chunk_size: int = GALLF_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN POOL + LAY under SDPA
    WHEN all budgets use CUDA-graph full-depth BoN+LAY (never KV)
    THEN return mean lp / tok/s / wall / gflops.
    """
    _ = chunk_size  # API parity with GRAPHF scorers
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            claim = seed + 1000 * b
            m = score_batch_graphf_arm(
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
