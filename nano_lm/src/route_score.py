"""Score H-ROUTE: short budget→GALL arm, long→GRAPHF/KV path."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from cpoolb_score import score_batch_cpoolb
from early_ops import EarlyGene
from flash_ops import gpt_neo_sdpa_context
from gall_score import score_batch_gall
from graph_score import score_batch_graph_arm
from graphf_score import score_batch_graphf
from kvsel_ops import SMOKE_BUDGETS, should_use_kv
from lay_ops import LayGene
from route_ops import ROUTE_CHUNK

__all__ = [
    "score_batch_route",
    "score_route_trio",
    "tip_row",
    "ROUTE_CHUNK",
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


def score_batch_route(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    early_gene: EarlyGene,
    pool_gene: Mapping[str, Any],
    lay: LayGene | Mapping[str, float | int],
    seed: int,
    kv_threshold: int,
    chunk_size: int = ROUTE_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN EARLY+LAY GALL arm and POOL+LAY GRAPHF path
    WHEN short budgets use GALL and long budgets use GRAPHF/KV
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
                    gene=pool_gene,
                    max_new=b,
                    seed=claim,
                    chunk_size=int(chunk_size),
                )
            else:
                m = score_batch_graph_arm(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=early_gene,
                    lay=lay,
                    max_new=b,
                    seed=claim,
                )
            rows.append(m)
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out


def score_route_trio(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    early_gene: EarlyGene,
    pool_gene: Mapping[str, Any],
    lay: LayGene | Mapping[str, float | int],
    kv_threshold: int,
    seed: int,
    chunk_size: int = ROUTE_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, dict[str, float]]:
    """Score pure GALL, pure GRAPHF, and ROUTE under the same claim seed."""
    gall = score_batch_gall(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=early_gene,
        lay=lay,
        seed=seed,
        chunk_size=chunk_size,
        budgets=budgets,
    )
    graphf = score_batch_graphf(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=pool_gene,
        lay=lay,
        seed=seed,
        kv_threshold=kv_threshold,
        chunk_size=chunk_size,
        budgets=budgets,
    )
    route = score_batch_route(
        teacher=teacher,
        student=student,
        prompts=prompts,
        early_gene=early_gene,
        pool_gene=pool_gene,
        lay=lay,
        seed=seed,
        kv_threshold=kv_threshold,
        chunk_size=chunk_size,
        budgets=budgets,
    )
    return {"H-GALL": gall, "H-GRAPHF": graphf, "H-ROUTE": route}
