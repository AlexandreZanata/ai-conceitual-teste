"""Score H-GALL: always CUDA-graph LAY arm (no KV/CHBAT) under SDPA."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from early_ops import EarlyGene
from flash_ops import gpt_neo_sdpa_context
from gall_ops import GALL_CHUNK
from graph_score import SMOKE_BUDGETS, score_batch_graph, score_batch_graph_arm
from lay_ops import LayGene

__all__ = [
    "score_batch_gall",
    "score_batch_graph",
    "tip_row",
    "GALL_CHUNK",
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


def score_batch_gall(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    lay: LayGene | Mapping[str, float | int],
    seed: int,
    chunk_size: int = GALL_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN EARLY + LAY under SDPA
    WHEN all budgets use CUDA-graph full-depth LAY (never KV)
    THEN return mean lp / tok/s / wall / gflops.
    """
    _ = chunk_size  # API parity with GRAPH scorers
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            claim = seed + 1000 * b
            m = score_batch_graph_arm(
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
