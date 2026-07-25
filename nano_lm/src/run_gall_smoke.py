"""Smoke H-GALL: graph-all-budgets vs tip GRAPH on B2."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from eval_decode import load_pair
from gall_ops import GALL_CHUNK
from gall_score import SMOKE_BUDGETS, score_batch_gall, score_batch_graph, tip_row
from lay_ops import clamp_lay_gene
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _lay_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HLAY_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing LAY util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "max_skip" not in gene or "lay_conf" not in gene:
        raise ValueError(f"LAY missing max_skip/lay_conf: {path}")
    return clamp_lay_gene(gene)


def _kv_threshold(out: Path, seed: int) -> int:
    path = out / f"HKVSEL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing KVSEL util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {path}")
    return int(gene["kv_threshold"])


def _load_texts(*paths: Path) -> list[str]:
    texts: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            texts.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return texts


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-GALL requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    from data_tiny import load_tokenizer

    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    raw = _load_texts(c["prompts"], c["fit_prompts"])
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        lay = _lay_gene(out, seed)
        thr = _kv_threshold(out, seed)
        gene = {**early, "n": 1, "temperature": 1e-6}
        claim = seed + 7474
        _, b2 = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        graphed = score_batch_graph(
            teacher=teacher,
            student=b2,
            prompts=prompts,
            gene=gene,
            lay=lay,
            seed=claim,
            kv_threshold=thr,
            chunk_size=GALL_CHUNK,
        )
        g_tip = {
            **gene,
            **lay,
            "kv_threshold": thr,
            "chunk_size": GALL_CHUNK,
            "backend": "sdpa+kvsel+cudagraph+chbat",
            "graph": "full-depth per-T capture (untimed)",
        }
        rows.append(tip_row("H-GRAPH", f"HGRAPH_gall_seed{seed}", graphed, seed, g_tip))
        torch.cuda.empty_cache()
        gall = score_batch_gall(
            teacher=teacher,
            student=b2,
            prompts=prompts,
            gene=gene,
            lay=lay,
            seed=claim,
            chunk_size=GALL_CHUNK,
        )
        g = {
            **gene,
            **lay,
            "kv_threshold": thr,
            "chunk_size": GALL_CHUNK,
            "backend": "sdpa+cudagraph-all",
            "graph": "full-depth per-T all budgets (never KV)",
        }
        row = tip_row("H-GALL", f"HGALL_seed{seed}", gall, seed, g)
        write_json(out / f"HGALL_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "gall_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": GALL_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "CUDA graph all budgets (never KV) vs GRAPH dual-budget",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "gall_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
