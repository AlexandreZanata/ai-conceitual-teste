"""Formal equal-budget smoke+: B2 KD vs H-SEL (promoted), 3 seeds."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from eval_student import eval_student_vs_teacher
from hyp_sel import run_h_sel
from load_model import resolve_device
from matrix_common import ROOT, REPO, write_json
from train_kd import train_kd


def formal_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "prompts": ROOT / "prompts/eval_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/formal-hsel-b2",
        "steps_kd": 120,
        "max_examples": 300,
        "seq_len": 128,
        "batch_size": 4,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 48,
        "sel_pop": 8,
        "sel_gens": 12,
        "mutate_scale": 0.015,
    }


def _eval(c: dict[str, Any], ckpt: Path, seed: int, family: str) -> dict:
    ev = eval_student_vs_teacher(
        student_ckpt=ckpt,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["prompts"],
        cache_dir=c["cache"],
        max_new_tokens=c["max_new_eval"],
        seed=seed,
        temperature=0.8,
        top_p=0.9,
    )
    ev["family"] = family
    return ev


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
        rows.append(_eval(c, b2, seed, "B2"))
        if device.type == "cuda":
            torch.cuda.empty_cache()

        hsel = c["out"] / f"HSEL_seed{seed}.pt"
        meta = run_h_sel(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            pop_size=c["sel_pop"],
            generations=c["sel_gens"],
            mutate_scale=c["mutate_scale"],
            seq_len=c["seq_len"],
            batch_size=c["batch_size"],
            max_examples=c["max_examples"],
            seed=seed,
            out_path=hsel,
        )
        write_json(c["out"] / f"HSEL_seed{seed}_train.json", meta)
        rows.append(_eval(c, hsel, seed, "H-SEL"))
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
