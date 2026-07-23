"""Formal-budget H-DECKL vs B4 (Pareto), shared B2 ckpts."""

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
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import _eval_b4, formal_cfg as hdeck_formal_cfg

TOP_K = 1
LAM = 0.15


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hdeckl"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    return base


def _eval_gene(c: dict[str, Any], ckpt: Path, gene: dict, seed: int) -> dict:
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
        "family": "H-DECKL",
        "label": f"HDECKL_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall_ms),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
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
        rows.append(_eval_b4(c, b2, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        meta = run_h_deckl(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            cache_dir=c["cache"],
            pop_size=c["dec_pop"],
            generations=c["dec_gens"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_fit"],
            seed=seed,
            top_k=TOP_K,
            lam=LAM,
            out_meta=c["out"] / f"HDECKL_seed{seed}_train.json",
        )
        row = _eval_gene(c, b2, meta["best_gene"], seed)
        row["wall_save"] = bool(meta["wall_save"])
        row["teacher_forwards"] = int(meta["teacher_forwards"])
        row["lam"] = LAM
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
