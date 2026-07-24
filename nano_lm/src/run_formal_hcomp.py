"""Formal-budget H-COMP vs H-EARLY (torch.compile; same tip genes)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from comp_ops import COMPILE_MODE, compile_student, warmup_student
from early_fit import fitness_early_detail
from eval_student import load_student_ckpt
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import ROOT, REPO, write_json
from run_formal_hearly import formal_cfg as hearly_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hearly_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcomp"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    return base


def _gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    meta = json.loads(path.read_text(encoding="utf-8"))
    gene = meta.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal EARLY missing best_gene: {path}")
    return gene


def _score_row(
    c: dict[str, Any],
    *,
    family: str,
    ckpt: Path,
    gene: dict,
    seed: int,
    compiled: bool,
) -> dict:
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    device = teacher.device
    student = load_student_ckpt(ckpt, teacher.tokenizer, device)
    if compiled:
        student = compile_student(student, mode=COMPILE_MODE)
        warmup_student(student, device, steps=3)
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    lp, wall = fitness_early_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new=c["max_new_eval"],
        seed=seed + 7777,
    )
    return {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
        "compiled": compiled,
        "compile_mode": COMPILE_MODE if compiled else "eager",
    }


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        gene = _gene(c["early_dir"], seed)
        rows.append(
            _score_row(
                c, family="H-EARLY", ckpt=b2, gene=gene, seed=seed, compiled=False
            )
        )
        rows.append(
            _score_row(
                c, family="H-COMP", ckpt=b2, gene=gene, seed=seed, compiled=True
            )
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in c.items()},
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
