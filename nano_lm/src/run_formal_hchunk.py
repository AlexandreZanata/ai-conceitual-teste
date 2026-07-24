"""Formal H-CHUNK: chunked KV prefill under FLASH on long eval prompts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from chunk_fit import (
    DEFAULT_CHUNK,
    LONG_TARGET_TOKENS,
    fitness_chunk_detail,
    long_prompts,
    tip_row,
)
from data_tiny import load_tokenizer
from eval_decode import load_pair
from flash_fit import fitness_flash_detail
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hflash import formal_cfg as hflash_formal_cfg
from short_fit import fitness_early_detail


def formal_cfg() -> dict[str, Any]:
    base = hflash_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hchunk"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


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
    early = _early_gene(c["early_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + 9191
    max_new = int(c["max_new_eval"])
    gene = {**early, "chunk_size": DEFAULT_CHUNK, "backend": "sdpa+chunk"}
    lp_e, wall_e, gf_e = fitness_early_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    lp_f, wall_f, gf_f = fitness_flash_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    lp_c, wall_c, gf_c = fitness_chunk_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        chunk_size=DEFAULT_CHUNK,
    )
    rows = [
        tip_row(
            "H-EARLY", f"HEARLY_chunk_formal_seed{seed}", lp_e, wall_e, gf_e, seed, early
        ),
        tip_row(
            "H-FLASH", f"HFLASH_chunk_formal_seed{seed}", lp_f, wall_f, gf_f, seed, early
        ),
        tip_row("H-CHUNK", f"HCHUNK_formal_seed{seed}", lp_c, wall_c, gf_c, seed, gene),
    ]
    for r in rows:
        r["n_prompts"] = len(prompts)
        r["target_tokens"] = LONG_TARGET_TOKENS
        r["chunk_size"] = DEFAULT_CHUNK
    write_json(c["out"] / f"HCHUNK_seed{seed}_eval.json", rows[-1])
    return rows


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
            "chunk_size": DEFAULT_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "backend": "gpt_neo_sdpa + chunked KV prefill",
            "n_prompts": len(prompts),
        },
    )
    print(
        json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
