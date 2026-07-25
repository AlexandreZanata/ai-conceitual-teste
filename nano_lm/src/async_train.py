"""H-ASYNC train: 1-deep pipeline — build(i+1) overlaps PIN train(i)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch

from async_cache import build_one_topk
from pin_ops import pin_records
from student_model import build_student, count_params
from top_ops import expand_topk_logits, ms_per_step
from train_kd import kd_loss

__all__ = ["train_async_pin"]


def train_async_pin(
    *,
    teacher: object,
    batches: list[torch.Tensor],
    vocab_size: int,
    device: torch.device,
    lr: float,
    seed: int,
    temperature: float,
    alpha: float,
    out_path: Path,
    top_k: int,
) -> dict[str, Any]:
    """
    GIVEN teacher + planned batches
    WHEN building top-k record i+1 on a side stream while training step i
    THEN return PIN-quality ckpt and end-to-end pipeline wall_s.
    """
    if not batches:
        raise ValueError("batches must be non-empty")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    student = build_student(vocab_size).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    use_cuda = device.type == "cuda"
    build_stream = torch.cuda.Stream() if use_cuda else None
    t0 = time.perf_counter()
    ready = _ready_rec(teacher, batches[0], top_k=top_k, pin=use_cuda)
    losses: list[float] = []
    n = len(batches)
    for i in range(n):
        nxt = None
        if i + 1 < n:
            nxt = _launch_build(
                teacher,
                batches[i + 1],
                top_k=top_k,
                stream=build_stream,
                use_cuda=use_cuda,
            )
        losses.append(
            _train_step(
                student,
                opt,
                ready,
                vocab_size=vocab_size,
                device=device,
                temperature=temperature,
                alpha=alpha,
                non_blocking=use_cuda,
            )
        )
        if nxt is not None:
            if use_cuda and build_stream is not None:
                build_stream.synchronize()
            ready = pin_records([nxt])[0] if use_cuda else nxt
    if use_cuda:
        torch.cuda.synchronize()
    wall_s = time.perf_counter() - t0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"model": student.state_dict(), "seed": seed, "hypothesis": "H-ASYNC"},
        out_path,
    )
    return {
        "hypothesis": "H-ASYNC",
        "params": count_params(student),
        "steps": n,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "e2e_wall_s": wall_s,
        "train_wall_s": wall_s,
        "ms_per_step": ms_per_step(wall_s=wall_s, steps=n),
        "out_path": str(out_path),
        "pinned": use_cuda,
    }


def _ready_rec(
    teacher: object, ids_cpu: torch.Tensor, *, top_k: int, pin: bool
) -> dict[str, torch.Tensor]:
    rec = build_one_topk(teacher, ids_cpu, top_k=top_k)
    return pin_records([rec])[0] if pin else rec


def _launch_build(
    teacher: object,
    ids_cpu: torch.Tensor,
    *,
    top_k: int,
    stream: torch.cuda.Stream | None,
    use_cuda: bool,
) -> dict[str, torch.Tensor]:
    if use_cuda and stream is not None:
        with torch.cuda.stream(stream):
            return build_one_topk(teacher, ids_cpu, top_k=top_k)
    return build_one_topk(teacher, ids_cpu, top_k=top_k)


def _train_step(
    student: torch.nn.Module,
    opt: torch.optim.Optimizer,
    rec: dict[str, torch.Tensor],
    *,
    vocab_size: int,
    device: torch.device,
    temperature: float,
    alpha: float,
    non_blocking: bool,
) -> float:
    opt.zero_grad(set_to_none=True)
    ids = rec["ids"].to(device, non_blocking=non_blocking)
    idx = rec["topk_idx"].to(device, non_blocking=non_blocking)
    val = rec["topk_val"].to(
        device=device, dtype=torch.float32, non_blocking=non_blocking
    )
    t_logits = expand_topk_logits(idx, val, vocab_size=vocab_size)
    s_logits = student(ids).logits
    loss = kd_loss(s_logits, t_logits, ids, temperature=temperature, alpha=alpha)
    loss.backward()
    opt.step()
    return float(loss.item())
