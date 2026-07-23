"""H-ROUT: conf-route frozen EARLY vs DECM tip genes per prompt."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from dec_fit_ops import decode_with_gene
from decode_early import decode_early
from early_ops import clamp_early_gene
from eval_student import load_student_ckpt, teacher_mean_logprob
from lat2_ops import clamp_gene_lat2
from load_model import load_causal_lm
from matrix_common import write_json
from rout_ops import DEFAULT_TAU, route_tip


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _load_gene(path: Path, key: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if key not in data:
        raise KeyError(f"missing {key} in {path}")
    return dict(data[key])


def prompt_confidence(student: Any, tok: Any, text: str, device: torch.device) -> float:
    """Max softmax mass on the last prompt token (routing signal)."""
    ids = tok.encode(text, return_tensors="pt").to(device)
    with torch.no_grad():
        logits = student(ids).logits[:, -1, :].float()
        return float(torch.softmax(logits, dim=-1).max().item())


def run_h_rout(
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
    tau: float = DEFAULT_TAU,
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
    routes: list[str] = []
    t0 = time.perf_counter()
    for i, text in enumerate(prompts):
        conf = prompt_confidence(student, tok, text, device)
        tip = route_tip(conf, tau=tau)
        routes.append(tip)
        t1 = time.perf_counter()
        if tip == "early":
            result = decode_early(
                student,
                tok,
                text,
                n=int(early_g["n"]),
                max_new_tokens=max_new,
                min_new=int(early_g["min_new"]),
                conf_threshold=float(early_g["conf_threshold"]),
                patience=int(early_g["patience"]),
                temperature=float(early_g["temperature"]),
                top_p=float(early_g["top_p"]),
                seed=seed + i,
                device=device,
            )
        else:
            result = decode_with_gene(
                decm_g, student, tok, text, max_new, seed + i, device
            )
        walls.append((time.perf_counter() - t1) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    meta = {
        "hypothesis": "H-ROUT",
        "tau": tau,
        "early_gene": early_g,
        "decm_gene": decm_g,
        "routes": routes,
        "early_rate": sum(1 for r in routes if r == "early") / max(len(routes), 1),
        "eval_fit": sum(scores) / max(len(scores), 1),
        "eval_wall_ms": sum(walls) / max(len(walls), 1),
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
