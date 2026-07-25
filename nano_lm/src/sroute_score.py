"""Score H-SROUTE: frozen SERVE recipe vs length-budget ROUTE."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from early_ops import EarlyGene
from kvsel_ops import SMOKE_BUDGETS
from lay_ops import LayGene
from route_score import score_batch_route
from serve_ops import SERVE_CHUNK
from serve_score import score_serve_candidates
from sroute_ops import SROUTE_CHUNK

__all__ = [
    "score_sroute_pair",
    "tip_row",
    "SROUTE_CHUNK",
    "SMOKE_BUDGETS",
]


def score_sroute_pair(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    early_gene: EarlyGene,
    pool_gene: Mapping[str, Any],
    lay: LayGene | Mapping[str, float | int],
    kv_threshold: int,
    seed: int,
    chunk_size: int = SROUTE_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[str, dict[str, float], dict[str, float]]:
    """
    GIVEN same tips/genes
    WHEN scoring frozen SERVE pick vs ROUTE
    THEN return (serve_recipe, serve_metrics, route_metrics).
    """
    recipe, serve, _ = score_serve_candidates(
        teacher=teacher,
        student=student,
        prompts=prompts,
        early_gene=early_gene,
        pool_gene=pool_gene,
        lay=lay,
        kv_threshold=kv_threshold,
        seed=seed,
        chunk_size=int(chunk_size),
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
        chunk_size=int(chunk_size),
        budgets=budgets,
    )
    return recipe, serve, route
