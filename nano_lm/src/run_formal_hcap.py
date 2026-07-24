"""Formal-budget H-CAP: hard caps on formal H-POOL tip genes."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from cap_ops import CAP_NEWS, apply_hard_caps
from dec_fit_ops import fitness_gene_detail
from hold_ops import assert_disjoint, load_prompt_ids
from lat2_ops import MIN_LAM
from lat_ops import latency_aware_score
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcap"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["pool_dir"] = REPO / "results/nano-lm/formal-hpool"
    return base


def _tip_gene(pool_dir: Path, seed: int) -> dict[str, Any]:
    path = pool_dir / f"HPOOL_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal H-POOL tip: {path}")
    meta = json.loads(path.read_text(encoding="utf-8"))
    gene = meta.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal POOL missing best_gene: {path}")
    return gene


def _eval_pool(c: dict[str, Any], ckpt: Path, gene: dict, seed: int) -> dict:
    from eval_decode import load_pair

    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    lp, wall = fitness_gene_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new=c["max_new_eval"],
        seed=seed + 7777,
    )
    return {
        "family": "H-POOL",
        "label": f"HPOOL_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
    }


def _eval_cap(c: dict[str, Any], ckpt: Path, tip: dict, seed: int) -> dict:
    from eval_decode import load_pair

    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    best: tuple[float, dict, int, float, float] | None = None
    for raw in CAP_NEWS:
        g, mn = apply_hard_caps(tip, raw)
        lp, wall = fitness_gene_detail(
            g,
            teacher=teacher,
            student=student,
            prompts=texts,
            max_new=mn,
            seed=seed + 7777,
        )
        score = latency_aware_score(lp, wall, MIN_LAM)
        if best is None or score > best[0]:
            best = (score, g, mn, lp, wall)
    assert best is not None
    _, g, mn, lp, wall = best
    return {
        "family": "H-CAP",
        "label": f"HCAP_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": g,
        "max_new_cap": int(mn),
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
        tip = _tip_gene(c["pool_dir"], seed)
        rows.append(_eval_pool(c, b2, tip, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        rows.append(_eval_cap(c, b2, tip, seed))
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
