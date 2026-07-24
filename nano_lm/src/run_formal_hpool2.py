"""Formal-budget H-POOL2 vs H-POOL (tighter search)."""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from dec_fit_ops import fitness_gene_detail
from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_deckl import run_h_deckl
from load_model import resolve_device
from matrix_common import REPO, write_json
from pool2_ops import POOL2_GENS_FORMAL, POOL2_POP_FORMAL, warm_start_pop2
from run_formal_hpool import formal_cfg as hpool_formal_cfg

TOP_K = 1
LAM = 0.15


def formal_cfg() -> dict[str, Any]:
    base = hpool_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hpool2"
    base["pool_dir"] = REPO / "results/nano-lm/formal-hpool"
    return base


def _eval_gene(
    c: dict[str, Any], ckpt: Path, gene: dict, seed: int, family: str
) -> dict:
    from eval_decode import load_pair

    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    lp, wall_ms = fitness_gene_detail(
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
        "mean_wall_ms": float(wall_ms),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
    }


def _tip_pool(pool_dir: Path, seed: int) -> tuple[dict, dict]:
    path = pool_dir / f"HPOOL_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal H-POOL tip: {path}")
    meta = json.loads(path.read_text(encoding="utf-8"))
    gene = meta.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal POOL missing best_gene: {path}")
    return gene, meta


def _cold_gene(pool_dir: Path, seed: int) -> dict:
    path = pool_dir / f"HDECKL_cold_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal cold DECKL: {path}")
    return json.loads(path.read_text(encoding="utf-8"))["best_gene"]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    pool_dir: Path = c["pool_dir"]
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        tip_gene, tip_meta = _tip_pool(pool_dir, seed)
        tip_row = _eval_gene(c, b2, tip_gene, seed, "H-POOL")
        tip_row["teacher_forwards"] = int(tip_meta.get("teacher_forwards", 0))
        attach_overfit(tip_row, float(tip_meta["best_fit"]))
        rows.append(tip_row)
        pool = [_cold_gene(pool_dir, s) for s in c["seeds"] if s != seed]
        init = warm_start_pop2(pool, POOL2_POP_FORMAL, random.Random(seed + 90))
        meta = run_h_deckl(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            cache_dir=c["cache"],
            pop_size=POOL2_POP_FORMAL,
            generations=POOL2_GENS_FORMAL,
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_fit"],
            seed=seed + 90,
            init_genes=init,
            hypothesis="H-POOL2",
            out_meta=c["out"] / f"HPOOL2_seed{seed}_train.json",
            top_k=TOP_K,
            lam=LAM,
        )
        row = _eval_gene(c, b2, meta["best_gene"], seed, "H-POOL2")
        row["teacher_forwards"] = int(meta["teacher_forwards"])
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
