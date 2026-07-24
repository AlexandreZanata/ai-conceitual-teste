"""Formal-budget H-POOL3 vs H-POOL tip (FLOP dual gate)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from decode_genes import clamp_gene
from eval_student import load_student_ckpt
from hyp_pool3 import run_h_pool3
from load_model import load_causal_lm, resolve_device
from matrix_common import ROOT, REPO, write_json
from pool3_ops import clamp_pool3_gene
from poolf_fit import fitness_poolf_detail
from run_formal_hpool import formal_cfg as hpool_formal_cfg

LAM = 0.4


def formal_cfg() -> dict[str, Any]:
    base = hpool_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hpool3"
    base["pool_dir"] = REPO / "results/nano-lm/formal-hpool"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    return base


def _tip_gene(pool_dir: Path, seed: int) -> dict[str, Any]:
    path = pool_dir / f"HPOOL_seed{seed}_train.json"
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal POOL missing best_gene: {path}")
    return gene


def _eval(
    family: str, label: str, gene: dict, teacher, student, prompts, max_new, seed, clamp_fn
) -> dict[str, Any]:
    lp, wall, gf = fitness_poolf_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 7777,
        clamp_fn=clamp_fn,
    )
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "mean_est_gflops": float(gf),
        "seed": seed,
        "best_gene": gene,
        "lam": LAM,
    }


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    claim = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    fit = c["fit_prompts"]
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    hold = int(c["max_new_eval"])
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        student = load_student_ckpt(b2, teacher.tokenizer, teacher.device)
        tip = _tip_gene(c["pool_dir"], seed)
        rows.append(
            _eval(
                "H-POOL", f"HPOOL_seed{seed}", tip, teacher, student, claim, hold, seed,
                clamp_gene,
            )
        )
        meta = run_h_pool3(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=fit,
            cache_dir=c["cache"],
            pop_size=c.get("dec_pop", 8),
            generations=c.get("dec_gens", 4),
            max_new=c.get("max_new_fit", 24),
            eval_max_new=hold,
            seed=seed,
            tip_gene=tip,
            lam=LAM,
            out_meta=c["out"] / f"HPOOL3_seed{seed}_train.json",
        )
        rows.append(
            _eval(
                "H-POOL3",
                f"HPOOL3_seed{seed}",
                meta["best_gene"],
                teacher,
                student,
                claim,
                hold,
                seed,
                clamp_pool3_gene,
            )
        )
        if device.type == "cuda":
            import torch

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
