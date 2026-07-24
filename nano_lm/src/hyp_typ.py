"""H-TYP: grid-search typical mass on B2 student; claim vs B4."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import yaml

from decode_typ import decode_typ
from eval_student import load_student_ckpt, teacher_mean_logprob
from load_model import load_causal_lm
from matrix_common import write_json
from typ_ops import TYP_MASSES, best_typ_index


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _score_typ(
    *,
    typ_mass: float,
    teacher: Any,
    student: Any,
    prompts: list[str],
    max_new: int,
    seed: int,
    temperature: float,
    top_p: float,
) -> tuple[float, float]:
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_typ(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=temperature,
            top_p=top_p,
            typ_mass=typ_mass,
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)


def run_h_typ(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new: int,
    seed: int,
    out_meta: Path,
    temperature: float = 0.8,
    top_p: float = 0.9,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    fit_prompts = _prompts(prompts_path)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    t0 = time.perf_counter()
    fit_lps: list[float] = []
    for j, mass in enumerate(TYP_MASSES):
        lp, _ = _score_typ(
            typ_mass=float(mass),
            teacher=teacher,
            student=student,
            prompts=fit_prompts,
            max_new=min(16, max_new),
            seed=seed + 100 * j,
            temperature=temperature,
            top_p=top_p,
        )
        fit_lps.append(lp)
    best_i = best_typ_index(fit_lps)
    best_m = float(TYP_MASSES[best_i])
    eval_lp, eval_wall = _score_typ(
        typ_mass=best_m,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
        temperature=temperature,
        top_p=top_p,
    )
    meta = {
        "hypothesis": "H-TYP",
        "typ_masses": list(TYP_MASSES),
        "fit_lps": fit_lps,
        "best_typ_mass": best_m,
        "best_fit": fit_lps[best_i],
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_max_new": hold,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
