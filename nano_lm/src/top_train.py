"""Live STAG KD control + H-TOP top-k cache train loops."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch

from student_model import build_student, count_params
from top_ops import expand_topk_logits, ms_per_step
from train_kd import kd_loss
from pin_ops import pin_records


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


def _to_device_rec(
    rec: dict[str, torch.Tensor],
    *,
    device: torch.device,
    vocab_size: int,
    non_blocking: bool,
) -> tuple[torch.Tensor, torch.Tensor]:
    ids = rec["ids"].to(device, non_blocking=non_blocking)
    idx = rec["topk_idx"].to(device, non_blocking=non_blocking)
    val = rec["topk_val"].to(
        device=device, dtype=torch.float32, non_blocking=non_blocking
    )
    return ids, expand_topk_logits(idx, val, vocab_size=vocab_size)


def _warmup_compile(
    *,
    student: torch.nn.Module,
    opt: torch.optim.Optimizer,
    rec: dict[str, torch.Tensor],
    device: torch.device,
    vocab_size: int,
    non_blocking: bool,
    temperature: float,
    alpha: float,
) -> None:
    """Untimed forward+backward to warm compile; discard grads (no opt.step)."""
    ids, t_logits = _to_device_rec(
        rec, device=device, vocab_size=vocab_size, non_blocking=non_blocking
    )
    opt.zero_grad(set_to_none=True)
    loss = kd_loss(
        student(ids).logits, t_logits, ids, temperature=temperature, alpha=alpha
    )
    loss.backward()
    opt.zero_grad(set_to_none=True)
    if device.type == "cuda":
        torch.cuda.synchronize()


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
    pinned: bool = False,
    compiled: bool = False,
    hypothesis: str = "H-TOP",
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    student = build_student(vocab_size).to(device)
    if compiled:
        student = torch.compile(student, mode="default")
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    use_pin = bool(pinned) and device.type == "cuda"
    recs = pin_records(records) if use_pin else records
    if compiled and recs:
        _warmup_compile(
            student=student,
            opt=opt,
            rec=recs[0],
            device=device,
            vocab_size=vocab_size,
            non_blocking=use_pin,
            temperature=temperature,
            alpha=alpha,
        )

    def steps_fn():
        for rec in recs:
            yield _to_device_rec(
                rec, device=device, vocab_size=vocab_size, non_blocking=use_pin
            )

    losses, wall_s = _train_loop(
        student=student,
        opt=opt,
        device=device,
        temperature=temperature,
        alpha=alpha,
        steps_fn=steps_fn,
    )
    bare = getattr(student, "_orig_mod", student)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"model": bare.state_dict(), "seed": seed, "hypothesis": hypothesis},
        out_path,
    )
    steps = len(records)
    return {
        "hypothesis": hypothesis,
        "params": count_params(bare),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "train_wall_s": wall_s,
        "ms_per_step": ms_per_step(wall_s=wall_s, steps=steps),
        "out_path": str(out_path),
        "pinned": use_pin,
        "compiled": bool(compiled),
    }
