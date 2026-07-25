"""Score frozen EARLY/POOL tip genes on live vs PRE3 ckpts for H-RETIP."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch

from dec_fit_ops import fitness_gene_detail
from decode_genes import clamp_gene
from early_fit import fitness_early_detail
from early_ops import clamp_early_gene
from eval_decode import load_pair

__all__ = ["load_best_gene", "score_early_on_ckpt", "score_pool_on_ckpt", "serve_pair"]


def load_best_gene(path: Path) -> dict[str, Any]:
    """Load best_gene from tip train/eval JSON."""
    if not path.is_file():
        raise FileNotFoundError(f"missing tip gene: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return gene


def score_early_on_ckpt(
    *,
    ckpt: Path,
    gene: dict[str, Any],
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> dict[str, float]:
    """Frozen EARLY gene on one student ckpt → mean_lp / mean_wall."""
    teacher, student = load_pair(ckpt, teacher_id, tokenizer_id, cache_dir)
    lp, wall = fitness_early_detail(
        clamp_early_gene(gene),
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed,
    )
    del student, teacher
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return {"mean_lp": float(lp), "mean_wall": float(wall)}


def score_pool_on_ckpt(
    *,
    ckpt: Path,
    gene: dict[str, Any],
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> dict[str, float]:
    """Frozen POOL gene on one student ckpt → mean_lp / mean_wall."""
    teacher, student = load_pair(ckpt, teacher_id, tokenizer_id, cache_dir)
    tip = clamp_gene(dict(gene))
    lp, wall = fitness_gene_detail(
        tip,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed,
    )
    del student, teacher
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return {"mean_lp": float(lp), "mean_wall": float(wall)}


def serve_pair(
    *,
    live_ckpt: Path,
    retip_ckpt: Path,
    early_gene: dict[str, Any],
    pool_gene: dict[str, Any],
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> dict[str, dict[str, float]]:
    """
    GIVEN matched live vs PRE3 ckpts + frozen tip genes
    WHEN scoring EARLY and POOL on both
    THEN return control/retip maps for decide_hretip.
    """
    # Reload teacher once per tip family to keep VRAM peaked but safe.
    early_c = score_early_on_ckpt(
        ckpt=live_ckpt,
        gene=early_gene,
        teacher_id=teacher_id,
        tokenizer_id=tokenizer_id,
        cache_dir=cache_dir,
        prompts=prompts,
        max_new=max_new,
        seed=seed,
    )
    early_r = score_early_on_ckpt(
        ckpt=retip_ckpt,
        gene=early_gene,
        teacher_id=teacher_id,
        tokenizer_id=tokenizer_id,
        cache_dir=cache_dir,
        prompts=prompts,
        max_new=max_new,
        seed=seed,
    )
    pool_c = score_pool_on_ckpt(
        ckpt=live_ckpt,
        gene=pool_gene,
        teacher_id=teacher_id,
        tokenizer_id=tokenizer_id,
        cache_dir=cache_dir,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 31,
    )
    pool_r = score_pool_on_ckpt(
        ckpt=retip_ckpt,
        gene=pool_gene,
        teacher_id=teacher_id,
        tokenizer_id=tokenizer_id,
        cache_dir=cache_dir,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 31,
    )
    return {
        "early_control": early_c,
        "early_retip": early_r,
        "pool_control": pool_c,
        "pool_retip": pool_r,
    }
