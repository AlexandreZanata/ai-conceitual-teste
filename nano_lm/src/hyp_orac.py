"""H-ORAC: decode both tips; teacher picks; charge winner wall only."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from dec_fit_ops import decode_with_gene
from decode_early import decode_early
from early_ops import clamp_early_gene
from eval_student import load_student_ckpt, teacher_mean_logprob
from lat2_ops import clamp_gene_lat2
from load_model import load_causal_lm
from matrix_common import write_json
from orac_ops import oracle_pick


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _load_gene(path: Path, key: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if key not in data:
        raise KeyError(f"missing {key} in {path}")
    return dict(data[key])


def _decode_early(student, tok, text, gene, max_new, seed, device):
    g = clamp_early_gene(gene)
    return decode_early(
        student,
        tok,
        text,
        n=int(g["n"]),
        max_new_tokens=max_new,
        min_new=int(g["min_new"]),
        conf_threshold=float(g["conf_threshold"]),
        patience=int(g["patience"]),
        temperature=float(g["temperature"]),
        top_p=float(g["top_p"]),
        seed=seed,
        device=device,
    )


def run_h_orac(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    early_gene_path: Path,
    decm_gene_path: Path,
    max_new: int,
    seed: int,
    out_meta: Path,
) -> dict[str, Any]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    tok = teacher.tokenizer
    device = teacher.device
    early_g = clamp_early_gene(_load_gene(early_gene_path, "best_gene"))
    decm_g = clamp_gene_lat2(_load_gene(decm_gene_path, "best_gene"))
    prompts = _prompts(prompts_path)
    scores: list[float] = []
    walls: list[float] = []
    picks: list[int] = []
    t0 = time.perf_counter()
    for i, text in enumerate(prompts):
        tip_scores: list[float] = []
        tip_walls: list[float] = []
        tip_ids: list[list[int]] = []
        for j, kind in enumerate(("early", "decm")):
            t1 = time.perf_counter()
            if kind == "early":
                result = _decode_early(
                    student, tok, text, early_g, max_new, seed + 10 * i + j, device
                )
            else:
                result = decode_with_gene(
                    decm_g, student, tok, text, max_new, seed + 10 * i + j, device
                )
            tip_walls.append((time.perf_counter() - t1) * 1000.0)
            ids = tok.encode(text, return_tensors="pt")
            tip_scores.append(
                teacher_mean_logprob(teacher, ids, list(result.token_ids))
            )
            tip_ids.append(list(result.token_ids))
        pick = oracle_pick(tip_scores)
        picks.append(pick)
        scores.append(tip_scores[pick])
        walls.append(tip_walls[pick])
        _ = tip_ids[pick]
    meta = {
        "hypothesis": "H-ORAC",
        "early_gene": early_g,
        "decm_gene": decm_g,
        "picks": picks,
        "early_pick_rate": sum(1 for p in picks if p == 0) / max(len(picks), 1),
        "eval_fit": sum(scores) / max(len(scores), 1),
        "eval_wall_ms": sum(walls) / max(len(walls), 1),
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
        "note": "oracle charges winner wall only (diagnostic dual-gate bound)",
    }
    write_json(out_meta, meta)
    return meta
