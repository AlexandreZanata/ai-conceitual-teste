"""STAG-recipe KD: live teacher vs offline soft-label cache."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch

from soft_ops import ms_per_step
from student_model import build_student, count_params
from train_kd import kd_loss


def _train_loop(
    *,
    student: torch.nn.Module,
    opt: torch.optim.Optimizer,
    device: torch.device,
    temperature: float,
    alpha: float,
    steps_fn,
) -> tuple[list[float], float]:
    losses: list[float] = []
    t0 = time.perf_counter()
    for step, (ids, t_logits) in enumerate(steps_fn()):
        opt.zero_grad(set_to_none=True)
        s_logits = student(ids).logits
        loss = kd_loss(
            s_logits, t_logits, ids, temperature=temperature, alpha=alpha
        )
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        if device.type == "cuda" and (step + 1) % 10 == 0:
            torch.cuda.empty_cache()
    if device.type == "cuda":
        torch.cuda.synchronize()
    return losses, time.perf_counter() - t0


def train_live_batches(
    *,
    teacher: Any,
    batches: list[torch.Tensor],
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
    tok_n = int(teacher.model.config.vocab_size)
    student = build_student(tok_n).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)

    def steps_fn():
        for ids_cpu in batches:
            ids = ids_cpu.to(device)
            with torch.no_grad():
                t_logits = teacher.model(ids).logits
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
        {"model": student.state_dict(), "seed": seed, "hypothesis": "H-STAG"},
        out_path,
    )
    steps = len(batches)
    return {
        "hypothesis": "H-STAG",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "train_wall_s": wall_s,
        "ms_per_step": ms_per_step(wall_s=wall_s, steps=steps),
        "out_path": str(out_path),
    }


def train_soft_cache(
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
            t_logits = rec["logits"].to(device=device, dtype=torch.float32)
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
        {"model": student.state_dict(), "seed": seed, "hypothesis": "H-SOFT"},
        out_path,
    )
    steps = len(records)
    return {
        "hypothesis": "H-SOFT",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "train_wall_s": wall_s,
        "ms_per_step": ms_per_step(wall_s=wall_s, steps=steps),
        "out_path": str(out_path),
    }
