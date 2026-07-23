"""Shared matrix config + helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent


def matrix_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "prompts": ROOT / "prompts/smoke_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/student-matrix",
        "steps_ce": 30,
        "steps_kd": 30,
        "steps_bon": 8,
        "steps_mae": 4,
        "max_examples": 80,
        "seq_len": 64,
        "batch_size": 2,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 32,
        "draft_len": 4,
        "bon_n_eval": 4,
        "lifetime_steps": 2,
        "elite_k": 2,
        "steps_ent": 30,
        "agree_weight": 0.1,
        "steps_ann": 30,
        "ann_temp_start": 2.0,
        "ann_temp_end": 1.0,
        "max_new_fit": 16,
        "tournament_k": 3,
        "niche_alpha": 1e-3,
        "mut_adapt_factor": 1.2,
        "age_layers": 2,
        "immigrants_per_gen": 1,
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def eval_ckpt(c: dict[str, Any], ckpt: Path | None, seed: int, family: str) -> dict:
    from eval_student import eval_student_vs_teacher

    ev = eval_student_vs_teacher(
        student_ckpt=ckpt,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["prompts"],
        cache_dir=c["cache"],
        max_new_tokens=c["max_new_eval"],
        seed=seed,
        temperature=0.8,
        top_p=0.9,
    )
    ev["family"] = family
    return ev
