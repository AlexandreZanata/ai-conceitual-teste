"""Formal-budget H-MID vs H-EARLY tip (FLOP dual gate)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from earf_fit import fitness_earf_detail
from early_ops import clamp_early_gene
from eval_student import load_student_ckpt
from hyp_mid import run_h_mid
from lat2_ops import MIN_LAM
from load_model import load_causal_lm, resolve_device
from matrix_common import ROOT, REPO, write_json
from mid_ops import clamp_mid_gene
from run_formal_hearly import formal_cfg as hearly_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hearly_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hmid"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    return base


def _tip_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal EARLY missing best_gene: {path}")
    return gene


def _eval(
    family: str, label: str, gene: dict, teacher, student, prompts, max_new, seed, clamp_fn
) -> dict[str, Any]:
    lp, wall, gf = fitness_earf_detail(
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
        "lam": MIN_LAM,
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
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    hold = int(c["max_new_eval"])
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        student = load_student_ckpt(b2, teacher.tokenizer, teacher.device)
        tip = _tip_gene(c["early_dir"], seed)
        rows.append(
            _eval(
                "H-EARLY", f"HEARLY_seed{seed}", tip, teacher, student, claim, hold, seed,
                clamp_early_gene,
            )
        )
        meta = run_h_mid(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=c["dec_pop"],
            generations=c["dec_gens"],
            max_new=c["max_new_fit"],
            eval_max_new=hold,
            seed=seed,
            tip_gene=tip,
            lam=MIN_LAM,
            out_meta=c["out"] / f"HMID_seed{seed}_train.json",
        )
        rows.append(
            _eval(
                "H-MID", f"HMID_seed{seed}", meta["best_gene"], teacher, student, claim,
                hold, seed, clamp_mid_gene,
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
