"""STAG-recipe KD from top-k soft-label cache."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from soft_train import _train_loop
from soft_ops import ms_per_step
from student_model import build_student, count_params
from top_ops import expand_topk_logits


def train_topk_cache(
    *,
    records: list[dict[str, torch.Tensor]],
    vocab_size: int,
    device: torch.device,
    lr: float,
    seed: int,
    temperature: float,
    alpha: float,
    out_path: Path,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    student = build_student(vocab_size).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)

    def steps_fn():
        for rec in records:
            ids = rec["ids"].to(device)
            idx = rec["topk_idx"].to(device)
            val = rec["topk_val"].to(device=device, dtype=torch.float32)
            t_logits = expand_topk_logits(idx, val, vocab_size=vocab_size)
            yield ids, t_logits

    losses, wall_s = _train_loop(
        student=student,
        opt=opt,
        device=device,
        temperature=temperature,
        alpha=alpha,
        steps_fn=steps_fn,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"model": student.state_dict(), "seed": seed, "hypothesis": "H-TOP"},
        out_path,
    )
    steps = len(records)
    return {
        "hypothesis": "H-TOP",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "train_wall_s": wall_s,
        "ms_per_step": ms_per_step(wall_s=wall_s, steps=steps),
        "out_path": str(out_path),
    }
