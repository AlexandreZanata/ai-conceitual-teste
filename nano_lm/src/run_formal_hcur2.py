"""Formal-budget H-CUR2: n_stages∈{2,3,4,5} equal KD steps."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from cur2_ops import CUR2_STAGES
from cur_ops import DEFAULT_SEQ_LO
from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import ROOT, REPO, eval_ckpt, write_json


def formal_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "prompts": ROOT / "prompts/eval_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/formal-hcur2",
        "steps_kd": 120,
        "max_examples": 300,
        "seq_len": 128,
        "batch_size": 4,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 48,
        "cur_seq_lo": DEFAULT_SEQ_LO,
    }


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        for n_stages in CUR2_STAGES:
            ckpt = c["out"] / f"HCUR2_n{n_stages}_seed{seed}.pt"
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
                seed=seed + 17 * int(n_stages),
                temperature=2.0,
                alpha=0.5,
                out_path=ckpt,
                seq_lo=int(c["cur_seq_lo"]),
                n_stages=int(n_stages),
            )
            write_json(
                c["out"] / f"HCUR2_n{n_stages}_seed{seed}_train.json", meta
            )
            ev = eval_ckpt(c, ckpt, seed, "H-CUR2")
            ev["n_stages"] = int(n_stages)
            ev["label"] = f"HCUR2_n{n_stages}_seed{seed}"
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
