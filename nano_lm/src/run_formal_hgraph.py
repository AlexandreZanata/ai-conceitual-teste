"""Formal H-GRAPH: CUDA-graph under LAYB vs tip LAYB on B2 (eval)."""

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
from graph_ops import GRAPH_CHUNK
from graph_score import SMOKE_BUDGETS, score_batch_graph, score_batch_layb, tip_row
from hold_ops import assert_disjoint, load_prompt_ids
from lay_ops import clamp_lay_gene
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, write_json
from run_formal_hlayb import formal_cfg as hlayb_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hlayb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hgraph"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


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
    c: dict[str, Any], seed: int, prompts: list[str], teacher: Any
) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    gene = _early_gene(c["early_dir"], seed)
    lay = _lay_gene(c["lay_dir"], seed)
    thr = _kv_threshold(c["kvsel_dir"], seed)
    _, b2 = load_pair(ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"])
    claim = seed + 10010
    layb = score_batch_layb(
        teacher=teacher,
        student=b2,
        prompts=prompts,
        gene=gene,
        lay=lay,
        seed=claim,
        kv_threshold=thr,
        chunk_size=GRAPH_CHUNK,
    )
    graphed = score_batch_graph(
        teacher=teacher,
        student=b2,
        prompts=prompts,
        gene=gene,
        lay=lay,
        seed=claim,
        kv_threshold=thr,
        chunk_size=GRAPH_CHUNK,
    )
    g_tip = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": GRAPH_CHUNK,
        "backend": "sdpa+kvsel+lay+chbat",
    }
    g = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": GRAPH_CHUNK,
        "backend": "sdpa+kvsel+cudagraph+chbat",
        "graph": "full-depth per-T capture (untimed)",
    }
    return [
        tip_row("H-LAYB", f"HLAYB_graph_formal_seed{seed}", layb, seed, g_tip),
        tip_row("H-GRAPH", f"HGRAPH_formal_seed{seed}", graphed, seed, g),
    ]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-GRAPH formal requires CUDA")
    c["out"].mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        _texts(c["prompts"]), tok, target_tokens=LONG_TARGET_TOKENS
    )
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, prompts, teacher))
        torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "n_prompts": len(prompts),
        "chunk_size": GRAPH_CHUNK,
        "budgets": list(SMOKE_BUDGETS),
        "target_tokens": LONG_TARGET_TOKENS,
        "mode": "CUDA graph full-depth LAY arm under LAYB; capture untimed; long eval",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
