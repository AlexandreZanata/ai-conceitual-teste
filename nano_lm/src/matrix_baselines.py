"""Matrix wave 1: baselines B0, B1 (CE), B2 (KD)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from matrix_common import eval_ckpt, write_json
from train_ce import train_ce
from train_kd import train_kd


def run_baselines(c: dict[str, Any], device: torch.device, rows: list) -> None:
    out: Path = c["out"]
    for seed in c["seeds"]:
        rows.append(eval_ckpt(c, None, seed, "B0"))

    for seed in c["seeds"]:
        ckpt = out / f"B1_seed{seed}.pt"
        meta = train_ce(
            steps=c["steps_ce"],
            batch_size=c["batch_size"],
            seq_len=c["seq_len"],
            max_examples=c["max_examples"],
            lr=c["lr"],
            seed=seed,
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            out_path=ckpt,
        )
        write_json(out / f"B1_seed{seed}_train.json", meta)
        rows.append(eval_ckpt(c, ckpt, seed, "B1"))

    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
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
            out_path=ckpt,
        )
        write_json(out / f"B2_seed{seed}_train.json", meta)
        rows.append(eval_ckpt(c, ckpt, seed, "B2"))
