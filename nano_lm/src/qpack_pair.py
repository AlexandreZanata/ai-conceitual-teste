"""Shared H-POOL / H-FLAYB seed pair for H-QPACK."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eval_decode import load_pair
from lay_ops import clamp_lay_gene
from poolb_score import throughput_gene
from qpack_ops import QPACK_CHUNK
from qpack_score import SMOKE_BUDGETS, score_qpack_pair, tip_row

__all__ = ["run_seed_pair", "QPACK_CHUNK", "SMOKE_BUDGETS"]


def _load_gene(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"missing gene file: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return gene


def _pool_gene(pool_dir: Path, seed: int) -> dict[str, Any]:
    eval_p = pool_dir / f"HPOOL_seed{seed}_eval.json"
    train_p = pool_dir / f"HPOOL_seed{seed}_train.json"
    path = eval_p if eval_p.is_file() else train_p
    return throughput_gene(_load_gene(path))


def _lay_gene(lay_dir: Path, seed: int) -> dict[str, Any]:
    gene = _load_gene(lay_dir / f"HLAY_seed{seed}_eval.json")
    if "max_skip" not in gene or "lay_conf" not in gene:
        raise ValueError(f"LAY missing max_skip/lay_conf: {lay_dir}")
    return clamp_lay_gene(gene)


def _kv_threshold(kvsel_dir: Path, seed: int) -> int:
    gene = _load_gene(kvsel_dir / f"HKVSEL_seed{seed}_eval.json")
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {kvsel_dir}")
    return int(gene["kv_threshold"])


def run_seed_pair(
    c: dict[str, Any],
    seed: int,
    prompts: list[str],
    *,
    claim_offset: int = 9933,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> list[dict[str, Any]]:
    """
    GIVEN shared B2 + tip genes
    WHEN scoring serial POOL vs FLAYB pack
    THEN return tip_row for H-POOL and H-FLAYB.
    """
    gene_dir = Path(c.get("gene_dir", c["out"]))
    pool_dir = Path(c.get("pool_dir", gene_dir))
    lay_dir = Path(c.get("lay_dir", gene_dir))
    kvsel_dir = Path(c.get("kvsel_dir", gene_dir))
    ckpt_dir = Path(c.get("ckpt_dir", gene_dir))
    pool = _pool_gene(pool_dir, seed)
    lay = _lay_gene(lay_dir, seed)
    thr = _kv_threshold(kvsel_dir, seed)
    ckpt = ckpt_dir / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + claim_offset
    pool_m, flayb = score_qpack_pair(
        teacher=teacher,
        student=student,
        prompts=prompts,
        pool_gene=pool,
        lay=lay,
        kv_threshold=thr,
        seed=claim,
        chunk_size=QPACK_CHUNK,
        budgets=budgets,
    )
    meta = {
        "kv_threshold": thr,
        "chunk_size": QPACK_CHUNK,
        "budgets": list(budgets),
    }
    return [
        tip_row(
            "H-POOL",
            f"HPOOL_qpack_seed{seed}",
            pool_m,
            seed,
            {**pool, **meta, "backend": "serial-pool"},
        ),
        tip_row(
            "H-FLAYB",
            f"HFLAYB_qpack_seed{seed}",
            flayb,
            seed,
            {**pool, **lay, **meta, "backend": "sdpa+kvsel+lay+cpoolb"},
        ),
    ]
