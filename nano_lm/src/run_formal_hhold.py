"""Formal equal-budget: B2 KD vs H-HOLD (holdout fitness), 3 seeds."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from eval_student import eval_student_vs_teacher
from hold_ops import attach_overfit
from hyp_hold import run_h_hold
from load_model import resolve_device
from matrix_common import ROOT, REPO, write_json
from train_kd import train_kd


def formal_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "fit_prompts": ROOT / "prompts/fit_prompts.yaml",
        "prompts": ROOT / "prompts/eval_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/formal-hhold-b2",
        "steps_kd": 120,
        "max_examples": 300,
        "seq_len": 128,
        "batch_size": 4,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 48,
        "max_new_fit": 24,
        "hold_pop": 8,
        "hold_gens": 12,
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

        hhold = c["out"] / f"HHOLD_seed{seed}.pt"
        meta = run_h_hold(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            fit_prompts_path=c["fit_prompts"],
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            device=device,
            pop_size=c["hold_pop"],
            generations=c["hold_gens"],
            mutate_scale=c["mutate_scale"],
            max_new_fit=c["max_new_fit"],
            seed=seed,
            out_path=hhold,
        )
        write_json(c["out"] / f"HHOLD_seed{seed}_train.json", meta)
        row = _eval(c, hhold, seed, "H-HOLD")
        attach_overfit(row, float(meta["best_fit"]))
        rows.append(row)
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
