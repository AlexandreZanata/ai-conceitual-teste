"""H-TMN: stack tip TYP × tip MINP; claim vs max tip."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json
from tmn_fit import fitness_tmn_detail


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_tmn(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new: int,
    seed: int,
    out_meta: Path,
    typ_train: Path,
    minp_train: Path,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    typ = json.loads(typ_train.read_text(encoding="utf-8"))
    minp = json.loads(minp_train.read_text(encoding="utf-8"))
    typ_mass = float(typ["best_typ_mass"])
    min_p = float(minp["best_min_p"])
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    t0 = time.perf_counter()
    eval_lp, eval_wall = fitness_tmn_detail(
        typ_mass=typ_mass,
        min_p=min_p,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-TMN",
        "typ_mass": typ_mass,
        "min_p": min_p,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_max_new": hold,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
        "typ_train": str(typ_train),
        "minp_train": str(minp_train),
    }
    write_json(out_meta, meta)
    return meta
