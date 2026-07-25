"""Formal H-GRAPHF: CUDA-graph under FLAYB vs tip FLAYB on B2 (eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from data_tiny import load_tokenizer
from eval_decode import load_pair
from graphf_ops import GRAPHF_CHUNK
from graphf_score import SMOKE_BUDGETS, score_batch_flayb, score_batch_graphf, tip_row
from hold_ops import assert_disjoint, load_prompt_ids
from lay_ops import clamp_lay_gene
from load_model import resolve_device
from matrix_common import REPO, write_json
from poolb_score import throughput_gene
from run_formal_hflayb import formal_cfg as hflayb_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hflayb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hgraphf"
    return base


def _pool_gene(pool_dir: Path, seed: int) -> dict[str, Any]:
    path = pool_dir / f"HPOOL_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal POOL tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"POOL missing best_gene: {path}")
    return throughput_gene(gene)


def _lay_gene(lay_dir: Path, seed: int) -> dict[str, Any]:
    path = lay_dir / f"HLAY_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal LAY: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "max_skip" not in gene or "lay_conf" not in gene:
        raise ValueError(f"LAY missing max_skip/lay_conf: {path}")
    return clamp_lay_gene(gene)


def _kv_threshold(kvsel_dir: Path, seed: int) -> int:
    path = kvsel_dir / f"HKVSEL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal KVSEL: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {path}")
    return int(gene["kv_threshold"])


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
    lay = _lay_gene(c["lay_dir"], seed)
    thr = _kv_threshold(c["kvsel_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + 10101
    flayb = score_batch_flayb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        lay=lay,
        seed=claim,
        kv_threshold=thr,
        chunk_size=GRAPHF_CHUNK,
    )
    graphed = score_batch_graphf(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        lay=lay,
        seed=claim,
        kv_threshold=thr,
        chunk_size=GRAPHF_CHUNK,
    )
    g_tip = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": GRAPHF_CHUNK,
        "backend": "sdpa+kvsel+lay+cpoolb",
    }
    g = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": GRAPHF_CHUNK,
        "backend": "sdpa+kvsel+cudagraph+cpoolb",
        "graph": "full-depth per-T capture (untimed)",
    }
    return [
        tip_row("H-FLAYB", f"HFLAYB_graphf_formal_seed{seed}", flayb, seed, g_tip),
        tip_row("H-GRAPHF", f"HGRAPHF_formal_seed{seed}", graphed, seed, g),
    ]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-GRAPHF formal requires CUDA")
    c["out"].mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        _texts(c["prompts"]), tok, target_tokens=LONG_TARGET_TOKENS
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, prompts))
        torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "n_prompts": len(prompts),
        "chunk_size": GRAPHF_CHUNK,
        "budgets": list(SMOKE_BUDGETS),
        "target_tokens": LONG_TARGET_TOKENS,
        "mode": "CUDA graph full-depth BoN+LAY arm under FLAYB; capture untimed; long eval",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
