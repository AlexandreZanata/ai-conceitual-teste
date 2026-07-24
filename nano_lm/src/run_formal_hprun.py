"""Formal H-PRUN: prune formal STAG → recovery; EARLY claim on eval_prompts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from eval_student import load_student_ckpt
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, ROOT, write_json
from prun_fit import row, score_early_flops
from prun_mask import sparsity_of
from prun_ops import DEFAULT_SPARSITY
from prun_recover import recover_pruned_kd
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg

TIP_STAGES = 4
RECOVER_STEPS = 60


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hprun"
    base["stag_dir"] = REPO / "results/nano-lm/formal-hstag"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    base["prompts"] = ROOT / "prompts/eval_prompts.yaml"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _run_seed(
    c: dict[str, Any], seed: int, teacher, prompts: list[str]
) -> list[dict[str, Any]]:
    early = _early_gene(c["early_dir"], seed)
    tip_ckpt = c["stag_dir"] / f"HSTAG_st{TIP_STAGES}_seed{seed}.pt"
    if not tip_ckpt.is_file():
        raise FileNotFoundError(f"missing formal STAG tip: {tip_ckpt}")
    tip_student = load_student_ckpt(tip_ckpt, teacher.tokenizer, teacher.device)
    claim = seed + 7777
    max_new = int(c["max_new_eval"])
    lp_t, wall_t, gf_t = score_early_flops(
        early,
        teacher=teacher,
        student=tip_student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=1.0,
    )
    tip_row = row(
        "H-STAG",
        f"HSTAG_prun_formal_seed{seed}",
        lp_t,
        wall_t,
        gf_t,
        seed,
        {"density": 1.0, "best_gene": early, "n_prompts": len(prompts)},
    )
    student = load_student_ckpt(tip_ckpt, teacher.tokenizer, teacher.device)
    prun_ckpt = c["out"] / f"HPRUN_seed{seed}.pt"
    meta = recover_pruned_kd(
        student=student,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=teacher.device,
        steps=RECOVER_STEPS,
        batch_size=int(c["batch_size"]),
        seq_len=int(c["seq_len"]),
        max_examples=int(c["max_examples"]),
        lr=float(c["lr"]),
        seed=seed + 17,
        temperature=2.0,
        alpha=0.5,
        sparsity=DEFAULT_SPARSITY,
        out_path=prun_ckpt,
    )
    write_json(c["out"] / f"HPRUN_seed{seed}_train.json", meta)
    dens = float(meta["density"])
    lp_p, wall_p, gf_p = score_early_flops(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=dens,
    )
    prun_row = row(
        "H-PRUN",
        f"HPRUN_formal_seed{seed}",
        lp_p,
        wall_p,
        gf_p,
        seed,
        {
            "density": dens,
            "sparsity": sparsity_of(student),
            "best_gene": early,
            "n_prompts": len(prompts),
        },
    )
    write_json(c["out"] / f"HPRUN_seed{seed}_eval.json", prun_row)
    return [tip_row, prun_row]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    prompts = _texts(c["prompts"])
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, teacher, prompts))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        c["out"] / "formal.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "sparsity_target": DEFAULT_SPARSITY,
            "recover_steps": RECOVER_STEPS,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
