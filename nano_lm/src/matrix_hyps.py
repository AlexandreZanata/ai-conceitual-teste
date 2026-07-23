"""Matrix wave 2: H-SEL, H-BON, H-MAE."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from hyp_bon import run_h_bon
from hyp_mae import run_h_mae
from hyp_sel import run_h_sel
from matrix_common import eval_ckpt, write_json


def run_hypotheses(c: dict[str, Any], device: torch.device, rows: list) -> None:
    out: Path = c["out"]
    for seed in c["seeds"]:
        ckpt = out / f"HSEL_seed{seed}.pt"
        meta = run_h_sel(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            pop_size=4,
            generations=3,
            mutate_scale=0.02,
            seq_len=c["seq_len"],
            batch_size=c["batch_size"],
            max_examples=c["max_examples"],
            seed=seed,
            out_path=ckpt,
        )
        write_json(out / f"HSEL_seed{seed}_train.json", meta)
        rows.append(eval_ckpt(c, ckpt, seed, "H-SEL"))

    for seed in c["seeds"]:
        ckpt = out / f"HBON_seed{seed}.pt"
        meta = run_h_bon(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            steps=c["steps_bon"],
            bon_n=4,
            max_new=16,
            seq_prompt=8,
            lr=c["lr"],
            seed=seed,
            temperature=0.8,
            top_p=0.9,
            out_path=ckpt,
        )
        write_json(out / f"HBON_seed{seed}_train.json", meta)
        rows.append(eval_ckpt(c, ckpt, seed, "H-BON"))

    _run_mae(c, device, rows)


def _run_mae(c: dict[str, Any], device: torch.device, rows: list) -> None:
    out: Path = c["out"]
    for seed in c["seeds"]:
        ckpt = out / f"HMAE_seed{seed}.pt"
        meta = run_h_mae(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            steps=c["steps_mae"],
            k=4,
            block=2,
            horizon=2,
            max_new=16,
            lr=c["lr"],
            seed=seed,
            temperature=0.8,
            top_p=0.9,
            out_path=ckpt,
        )
        write_json(out / f"HMAE_seed{seed}_train.json", meta)
        rows.append(eval_ckpt(c, ckpt, seed, "H-MAE"))
