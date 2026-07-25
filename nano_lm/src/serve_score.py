"""Score H-SERVE: EARLY alone vs speed (GALL) and quality (GRAPHF) stacks."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import score_serial_early, tip_row
from early_ops import EarlyGene
from gall_score import SMOKE_BUDGETS, score_batch_gall
from graphf_score import score_batch_graphf
from lay_ops import LayGene
from serve_ops import SERVE_CHUNK, pick_serve_recipe

__all__ = [
    "score_early_budgets",
    "score_serve_candidates",
    "tip_row",
    "SERVE_CHUNK",
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


def score_early_budgets(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    seed: int,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN EARLY tip gene alone (serial decode)
    WHEN scoring across the same budgets as serving stacks
    THEN return mean lp / tok/s / wall / gflops.
    """
    rows: list[dict[str, float]] = []
    for b in budgets:
        claim = seed + 1000 * b
        rows.append(
            score_serial_early(
                teacher=teacher,
                student=student,
                prompts=prompts,
                gene=gene,
                max_new=b,
                seed=claim,
            )
        )
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out


def score_serve_candidates(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    early_gene: EarlyGene,
    pool_gene: Mapping[str, Any],
    lay: LayGene | Mapping[str, float | int],
    kv_threshold: int,
    seed: int,
    chunk_size: int = SERVE_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[str, dict[str, float], dict[str, dict[str, float]]]:
    """
    GIVEN EARLY tip alone + speed (GALL) + quality (GRAPHF) candidates
    WHEN picking the better stack under the SERVE gate
    THEN return (recipe, chosen metrics, all candidate metrics).
    """
    early = score_early_budgets(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=early_gene,
        seed=seed,
        budgets=budgets,
    )
    speed = score_batch_gall(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=early_gene,
        lay=lay,
        seed=seed,
        chunk_size=chunk_size,
        budgets=budgets,
    )
    quality = score_batch_graphf(
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
    cands = {"speed": speed, "quality": quality}
    recipe = pick_serve_recipe(cands, early_lp=float(early["mean_lp"]))
    chosen = dict(cands[recipe])
    chosen["recipe"] = 1.0 if recipe == "speed" else 2.0
    return recipe, chosen, {"early": early, "speed": speed, "quality": quality}
