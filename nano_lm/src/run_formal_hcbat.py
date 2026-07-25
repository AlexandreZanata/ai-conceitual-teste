"""Formal H-CBAT: chunked BAT vs flat BAT (eval_prompts, long)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from bat_score import score_batch_early
from cbat_score import DEFAULT_CHUNK, score_batch_cbat, tip_row
from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from data_tiny import load_tokenizer
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hbat import formal_cfg as hbat_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hbat_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcbat"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


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
    gene = _early_gene(c["early_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + 9101
    max_new = int(c["max_new_eval"])
    bat = score_batch_early(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
    )
    bat["n_prompts"] = float(len(prompts))
    cbat = score_batch_cbat(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=max_new,
        seed=claim,
        chunk_size=DEFAULT_CHUNK,
    )
    cbat["n_prompts"] = float(len(prompts))
    g = {**gene, "chunk_size": DEFAULT_CHUNK, "backend": "sdpa+chunk+bat"}
    return [
        tip_row("H-BAT", f"HBAT_cbat_formal_seed{seed}", bat, seed, gene),
        tip_row("H-CBAT", f"HCBAT_formal_seed{seed}", cbat, seed, g),
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
        "chunk_size": DEFAULT_CHUNK,
        "target_tokens": LONG_TARGET_TOKENS,
        "mode": "tip-exit knobs; n=1 near-greedy; long eval",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
