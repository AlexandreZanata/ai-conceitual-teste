"""Formal H-FLAYB: LAY under FCPOOLB vs tip FCPOOLB (eval, dual budget)."""

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
from flayb_ops import FLAYB_CHUNK
from flayb_score import SMOKE_BUDGETS, score_batch_fcpoolb, score_batch_flayb, tip_row
from hold_ops import assert_disjoint, load_prompt_ids
from lay_ops import clamp_lay_gene
from load_model import resolve_device
from matrix_common import REPO, write_json
from poolb_score import throughput_gene
from run_formal_hfcpoolb import formal_cfg as hfcpoolb_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hfcpoolb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hflayb"
    base["lay_dir"] = REPO / "results/nano-lm/formal-hlay"
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
    claim = seed + 9606
    fcpoolb = score_batch_fcpoolb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        seed=claim,
        kv_threshold=thr,
        chunk_size=FLAYB_CHUNK,
    )
    flayb = score_batch_flayb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        lay=lay,
        seed=claim,
        kv_threshold=thr,
        chunk_size=FLAYB_CHUNK,
    )
    g_tip = {
        **gene,
        "kv_threshold": thr,
        "chunk_size": FLAYB_CHUNK,
        "backend": "sdpa+kvsel+cpoolb",
    }
    g = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": FLAYB_CHUNK,
        "backend": "sdpa+kvsel+lay+cpoolb",
    }
    return [
        tip_row("H-FCPOOLB", f"HFCPOOLB_flayb_formal_seed{seed}", fcpoolb, seed, g_tip),
        tip_row("H-FLAYB", f"HFLAYB_formal_seed{seed}", flayb, seed, g),
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
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "n_prompts": len(prompts),
        "chunk_size": FLAYB_CHUNK,
        "budgets": list(SMOKE_BUDGETS),
        "target_tokens": LONG_TARGET_TOKENS,
        "mode": "dual-budget LAY under FCPOOLB; n=1 near-greedy; long eval",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
