"""Formal H-CPOOLB: chunked POOLB vs flat POOLB (eval_prompts, long)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from cpoolb_ops import CPOOLB_CHUNK
from cpoolb_score import score_batch_cpoolb, tip_row
from data_tiny import load_tokenizer
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from poolb_score import score_batch_pool, throughput_gene
from run_formal_hpoolb import formal_cfg as hpoolb_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hpoolb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcpoolb"
    return base


def _pool_gene(pool_dir: Path, seed: int) -> dict[str, Any]:
    path = pool_dir / f"HPOOL_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal POOL tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"POOL missing best_gene: {path}")
    return throughput_gene(gene)


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _run_seed(
    c: dict[str, Any], seed: int, prompts: list[str]
) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    gene = _pool_gene(c["pool_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + 9202
    max_new = int(c["max_new_eval"])
    poolb = score_batch_pool(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
    )
    poolb["n_prompts"] = float(len(prompts))
    cpoolb = score_batch_cpoolb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
        chunk_size=CPOOLB_CHUNK,
    )
    cpoolb["n_prompts"] = float(len(prompts))
    g = {**gene, "chunk_size": CPOOLB_CHUNK, "backend": "sdpa+chunk+poolb"}
    return [
        tip_row("H-POOLB", f"HPOOLB_cpoolb_formal_seed{seed}", poolb, seed, gene),
        tip_row("H-CPOOLB", f"HCPOOLB_formal_seed{seed}", cpoolb, seed, g),
    ]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        _texts(c["prompts"]), tok, target_tokens=LONG_TARGET_TOKENS
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, prompts))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        c["out"] / "formal.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": CPOOLB_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "POOL tip top_p; n=1 near-greedy; long eval",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
