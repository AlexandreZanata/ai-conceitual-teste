"""Formal-budget H-PROX vs H-POOL (CE proxy fit; teacher claim)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from dec_fit_ops import fitness_gene_detail
from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_deckl import run_h_deckl
from hyp_prox import run_h_prox
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hpool import formal_cfg as hpool_formal_cfg

TOP_K = 1
LAM = 0.15


def formal_cfg() -> dict[str, Any]:
    base = hpool_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hprox"
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


def _attach(row: dict, meta: dict) -> dict:
    row["teacher_forwards"] = int(meta.get("teacher_forwards", 0))
    row["search_wall_s"] = float(meta.get("search_wall_s", meta.get("wall_s", 0.0)))
    row["warm_start"] = bool(meta.get("warm_start"))
    attach_overfit(row, float(meta["best_fit"]))
    return row


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    cold_genes: dict[int, dict] = {}
    t0 = time.perf_counter()
    common = dict(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["fit_prompts"],
        cache_dir=c["cache"],
        pop_size=c["dec_pop"],
        generations=c["dec_gens"],
        max_new=c["max_new_fit"],
        eval_max_new=c["max_new_fit"],
    )
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        meta = run_h_deckl(
            student_ckpt=b2,
            seed=seed,
            out_meta=c["out"] / f"HDECKL_cold_seed{seed}_train.json",
            top_k=TOP_K,
            lam=LAM,
            **common,
        )
        cold_genes[seed] = meta["best_gene"]
        if device.type == "cuda":
            torch.cuda.empty_cache()
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        pool = [cold_genes[s] for s in c["seeds"] if s != seed]
        pool_meta = run_h_deckl(
            student_ckpt=b2,
            seed=seed + 50,
            init_genes=pool,
            hypothesis="H-POOL",
            out_meta=c["out"] / f"HPOOL_seed{seed}_train.json",
            top_k=TOP_K,
            lam=LAM,
            **common,
        )
        rows.append(
            _attach(_eval_gene(c, b2, pool_meta["best_gene"], seed, "H-POOL"), pool_meta)
        )
        prox_meta = run_h_prox(
            student_ckpt=b2,
            seed=seed + 70,
            init_genes=pool,
            eval_prompts_path=c["prompts"],
            eval_max_new=c["max_new_eval"],
            out_meta=c["out"] / f"HPROX_seed{seed}_train.json",
            **common,
        )
        rows.append(
            _attach(_eval_gene(c, b2, prox_meta["best_gene"], seed, "H-PROX"), prox_meta)
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
