"""H-PRE train: pinned TOP cache with 1-deep H2D prefetch stream."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import torch

from pin_ops import pin_records
from student_model import build_student, count_params
from top_ops import ms_per_step
from top_train import _to_device_rec
from train_kd import kd_loss

__all__ = ["train_topk_prefetch"]


def train_topk_prefetch(
    *,
    records: list[dict[str, torch.Tensor]],
    vocab_size: int,
    device: torch.device,
    lr: float,
    seed: int,
    temperature: float,
    alpha: float,
    out_path: Path,
    hypothesis: str = "H-PRE",
    half_h2d: bool = False,
    fused_adam: bool = False,
    build_fn: Callable[[int], object] = build_student,
) -> dict[str, Any]:
    """
    GIVEN pinned top-k cache records on CUDA
    WHEN H2D+expand of step i+1 overlaps compute of step i
    THEN return PIN-quality ckpt and train ms/step.
    """
    if device.type != "cuda":
        raise ValueError("train_topk_prefetch requires CUDA")
    if not records:
        raise ValueError("records must be non-empty")
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    student = build_fn(vocab_size).to(device)
    student.train()
    if fused_adam:
        opt = torch.optim.AdamW(student.parameters(), lr=lr, fused=True)
    else:
        opt = torch.optim.AdamW(student.parameters(), lr=lr)
    recs = pin_records(records)
    to_dev = _to_device_rec
    if half_h2d:
        from half_ops import to_device_rec_half

        to_dev = to_device_rec_half
    copy_stream = torch.cuda.Stream()
    losses: list[float] = []
    t0 = time.perf_counter()
    with torch.cuda.stream(copy_stream):
        cur = to_dev(
            recs[0], device=device, vocab_size=vocab_size, non_blocking=True
        )
    torch.cuda.current_stream().wait_stream(copy_stream)
    n = len(recs)
    for i in range(n):
        nxt = None
        if i + 1 < n:
            with torch.cuda.stream(copy_stream):
                nxt = to_dev(
                    recs[i + 1],
                    device=device,
                    vocab_size=vocab_size,
                    non_blocking=True,
                )
        ids, t_logits = cur
        opt.zero_grad(set_to_none=True)
        loss = kd_loss(
            student(ids).logits,
            t_logits,
            ids,
            temperature=temperature,
            alpha=alpha,
        )
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        if nxt is not None:
            torch.cuda.current_stream().wait_stream(copy_stream)
            cur = nxt
        if (i + 1) % 10 == 0:
            torch.cuda.empty_cache()
    torch.cuda.synchronize()
    wall_s = time.perf_counter() - t0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"model": student.state_dict(), "seed": seed, "hypothesis": hypothesis},
        out_path,
    )
    return {
        "hypothesis": hypothesis,
        "params": count_params(student),
        "steps": n,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "train_wall_s": wall_s,
        "ms_per_step": ms_per_step(wall_s=wall_s, steps=n),
        "out_path": str(out_path),
        "pinned": True,
        "prefetch": True,
        "half_h2d": bool(half_h2d),
        "fused_adam": bool(fused_adam),
    }
