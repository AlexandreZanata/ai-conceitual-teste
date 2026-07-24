"""Formal-budget H-CACHE: tip EARLY genes + KV on formal B2 vs B4."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from cache_fit import fitness_cache_detail
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import _eval_b4, formal_cfg as hdeck_formal_cfg
from run_formal_hearly import _eval_gene as _eval_early_gene


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcache"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    return base


def _tip_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal H-EARLY tip: {path}")
    meta = json.loads(path.read_text(encoding="utf-8"))
    gene = meta.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal EARLY missing best_gene: {path}")
    return gene


def _eval_cache(c: dict[str, Any], ckpt: Path, gene: dict, seed: int) -> dict:
    from eval_decode import load_pair

    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    lp, wall_ms = fitness_cache_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new=c["max_new_eval"],
        seed=seed + 7777,
    )
    return {
        "family": "H-CACHE",
        "label": f"HCACHE_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall_ms),
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
        "use_kv_cache": True,
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
        gene = _tip_gene(c["early_dir"], seed)
        rows.append(_eval_b4(c, b2, seed))
        rows.append(_eval_early_gene(c, b2, gene, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        rows.append(_eval_cache(c, b2, gene, seed))
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
