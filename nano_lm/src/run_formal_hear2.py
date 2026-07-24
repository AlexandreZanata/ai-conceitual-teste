"""Formal-budget H-EAR2 vs H-EARLY tip (widened early gene)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from ear2_fit import fitness_ear2_detail
from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_ear2 import run_h_ear2
from lat2_ops import MIN_LAM
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hearly import _eval_gene as _eval_early_gene
from run_formal_hearly import formal_cfg as hearly_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hearly_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hear2"
    return base


def _eval_ear2(c: dict[str, Any], ckpt: Path, gene: dict, seed: int) -> dict:
    from eval_decode import load_pair

    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    lp, wall_ms = fitness_ear2_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new_ceiling=c["max_new_eval"],
        seed=seed + 7777,
    )
    return {
        "family": "H-EAR2",
        "label": f"HEAR2_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall_ms),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
    }


def _tip_early(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal H-EARLY tip: {path}")
    meta = json.loads(path.read_text(encoding="utf-8"))
    gene = meta.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal EARLY missing best_gene: {path}")
    return gene


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    early_dir = REPO / "results/nano-lm/formal-hearly"
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        tip = _tip_early(early_dir, seed)
        rows.append(_eval_early_gene(c, b2, tip, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        meta = run_h_ear2(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=c["dec_pop"],
            generations=c["dec_gens"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_eval"],
            seed=seed,
            lam=MIN_LAM,
            out_meta=c["out"] / f"HEAR2_seed{seed}_train.json",
        )
        row = _eval_ear2(c, b2, meta["best_gene"], seed)
        row["lam"] = MIN_LAM
        attach_overfit(row, float(meta["best_fit"]))
        rows.append(row)
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
