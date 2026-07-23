"""Formal-budget H-LOT vs B2 (lottery ticket), equal KD steps."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from hyp_lot import run_h_lot
from load_model import resolve_device
from matrix_common import ROOT, REPO, eval_ckpt, write_json
from train_kd import train_kd


def formal_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "prompts": ROOT / "prompts/eval_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/formal-hlot",
        "steps_kd": 120,
        "max_examples": 300,
        "seq_len": 128,
        "batch_size": 4,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 48,
        "lot_keep_frac": 0.3,
    }


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        b2 = c["out"] / f"B2_seed{seed}.pt"
        meta = train_kd(
            teacher_id=c["teacher_id"],
            steps=c["steps_kd"],
            batch_size=c["batch_size"],
            seq_len=c["seq_len"],
            max_examples=c["max_examples"],
            lr=c["lr"],
            seed=seed,
            temperature=2.0,
            alpha=0.5,
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            out_path=b2,
        )
        write_json(c["out"] / f"B2_seed{seed}_train.json", meta)
        rows.append(eval_ckpt(c, b2, seed, "B2"))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        ckpt = c["out"] / f"HLOT_seed{seed}.pt"
        lot_meta = run_h_lot(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            steps=c["steps_kd"],
            batch_size=c["batch_size"],
            seq_len=c["seq_len"],
            max_examples=c["max_examples"],
            lr=c["lr"],
            seed=seed,
            temperature=2.0,
            alpha=0.5,
            out_path=ckpt,
            keep_frac=float(c["lot_keep_frac"]),
        )
        write_json(c["out"] / f"HLOT_seed{seed}_train.json", lot_meta)
        ev = eval_ckpt(c, ckpt, seed, "H-LOT")
        ev["keep_frac"] = float(lot_meta["keep_frac_actual"])
        rows.append(ev)
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
