"""Formal H-CHB: frozen smoke chunk_size vs H-CHUNK tip (eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from chb_ops import DEFAULT_CHUNK
from chunk_fit import (
    LONG_TARGET_TOKENS,
    fitness_chunk_detail,
    long_prompts,
    tip_row,
)
from data_tiny import load_tokenizer
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hchunk import formal_cfg as hchunk_formal_cfg
from short_fit import fitness_early_detail


def formal_cfg() -> dict[str, Any]:
    base = hchunk_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hchb"
    base["smoke_dir"] = REPO / "results/nano-lm/student-matrix"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _smoke_chunk_size(smoke_dir: Path, seed: int) -> int:
    path = smoke_dir / f"HCHB_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing CHB smoke: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "chunk_size" not in gene:
        raise ValueError(f"CHB smoke missing chunk_size: {path}")
    return int(gene["chunk_size"])


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
    best_b = _smoke_chunk_size(c["smoke_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + 9393
    max_new = int(c["max_new_eval"])
    kw = dict(
        teacher=teacher, student=student, prompts=prompts, max_new=max_new, seed=claim
    )
    lp_e, wall_e, gf_e = fitness_early_detail(early, **kw)
    lp_t, wall_t, gf_t = fitness_chunk_detail(
        early, chunk_size=DEFAULT_CHUNK, **kw
    )
    lp_u, wall_u, gf_u = fitness_chunk_detail(early, chunk_size=best_b, **kw)
    tip_g = {**early, "chunk_size": DEFAULT_CHUNK, "backend": "sdpa+chunk"}
    win_g = {**early, "chunk_size": best_b, "backend": "sdpa+chunk+sweep"}
    rows = [
        tip_row(
            "H-EARLY", f"HEARLY_chb_formal_seed{seed}", lp_e, wall_e, gf_e, seed, early
        ),
        tip_row(
            "H-CHUNK", f"HCHUNK_chb_formal_seed{seed}", lp_t, wall_t, gf_t, seed, tip_g
        ),
        tip_row("H-CHB", f"HCHB_formal_seed{seed}", lp_u, wall_u, gf_u, seed, win_g),
    ]
    for r in rows:
        r["n_prompts"] = len(prompts)
        r["target_tokens"] = LONG_TARGET_TOKENS
        r["chunk_size"] = int(r["best_gene"].get("chunk_size", DEFAULT_CHUNK))
    write_json(c["out"] / f"HCHB_seed{seed}_eval.json", rows[-1])
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
            "tip_chunk_size": DEFAULT_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "backend": "frozen smoke chunk_size vs tip",
            "n_prompts": len(prompts),
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
