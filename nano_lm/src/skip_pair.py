"""Shared H-BAT / H-CBAT / H-SKIP seed trio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bat_score import score_batch_early, tip_row
from cbat_score import DEFAULT_CHUNK, score_batch_cbat
from eval_decode import load_pair
from skip_ops import SKIP_CHUNK

__all__ = ["run_seed_trio", "SKIP_CHUNK", "DEFAULT_CHUNK"]


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip gene: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


def run_seed_trio(
    c: dict[str, Any],
    seed: int,
    prompts: list[str],
    *,
    claim_offset: int = 9595,
) -> list[dict[str, Any]]:
    """
    GIVEN shared B2 + EARLY tip
    WHEN scoring flat BAT, CBAT (FLAG), and SKIP=CHBAT chunk
    THEN return tip_row for H-BAT, H-CBAT, H-SKIP.
    """
    gene_dir = Path(c.get("gene_dir", c["out"]))
    early_dir = Path(c.get("early_dir", gene_dir))
    ckpt_dir = Path(c.get("ckpt_dir", gene_dir))
    gene = _early_gene(early_dir, seed)
    ckpt = ckpt_dir / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + claim_offset
    max_new = int(c["max_new_eval"])
    bat = score_batch_early(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
    )
    bat["n_prompts"] = float(len(prompts))
    cbat = score_batch_cbat(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
        chunk_size=DEFAULT_CHUNK,
    )
    cbat["n_prompts"] = float(len(prompts))
    skip = score_batch_cbat(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
        chunk_size=SKIP_CHUNK,
    )
    skip["n_prompts"] = float(len(prompts))
    return [
        tip_row(
            "H-BAT",
            f"HBAT_skip_seed{seed}",
            bat,
            seed,
            {**gene, "backend": "sdpa+bat"},
        ),
        tip_row(
            "H-CBAT",
            f"HCBAT_skip_seed{seed}",
            cbat,
            seed,
            {**gene, "chunk_size": DEFAULT_CHUNK, "backend": "sdpa+chunk+bat"},
        ),
        tip_row(
            "H-SKIP",
            f"HSKIP_seed{seed}",
            skip,
            seed,
            {
                **gene,
                "chunk_size": SKIP_CHUNK,
                "backend": "sdpa+chunk+bat+chb; skip-cbat",
            },
        ),
    ]
