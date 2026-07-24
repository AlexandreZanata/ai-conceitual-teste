"""Formal-budget H-CURT vs H-CUR (adopted tip knobs), equal steps."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from curt_ops import CURT_SEQ_LO, CURT_STAGES
from cur_ops import DEFAULT_SEQ_LO, N_STAGES
from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import ROOT, REPO, eval_ckpt, write_json


def formal_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "prompts": ROOT / "prompts/eval_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/formal-hcurt",
        "steps_kd": 120,
        "max_examples": 300,
        "seq_len": 128,
        "batch_size": 4,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 48,
    }


def _train_cur(
    c: dict[str, Any],
    device: torch.device,
    seed: int,
    *,
    family: str,
    seq_lo: int,
    n_stages: int,
    seed_off: int,
) -> dict[str, Any]:
    ckpt = c["out"] / f"{family.replace('-', '')}_seed{seed}.pt"
    meta = run_h_cur(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=device,
        steps=c["steps_kd"],
        batch_size=c["batch_size"],
        seq_len=c["seq_len"],
        max_examples=c["max_examples"],
        lr=c["lr"],
        seed=seed + seed_off,
        temperature=2.0,
        alpha=0.5,
        out_path=ckpt,
        seq_lo=seq_lo,
        n_stages=n_stages,
    )
    write_json(c["out"] / f"{family.replace('-', '')}_seed{seed}_train.json", meta)
    ev = eval_ckpt(c, ckpt, seed, family)
    ev["seq_lo"] = seq_lo
    ev["n_stages"] = n_stages
    return ev


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.append(
            _train_cur(
                c,
                device,
                seed,
                family="H-CUR",
                seq_lo=DEFAULT_SEQ_LO,
                n_stages=N_STAGES,
                seed_off=0,
            )
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
        rows.append(
            _train_cur(
                c,
                device,
                seed,
                family="H-CURT",
                seq_lo=CURT_SEQ_LO,
                n_stages=CURT_STAGES,
                seed_off=101,
            )
        )
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
