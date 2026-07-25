"""H-PRE train: pinned TOP cache with 1- or 2-deep H2D prefetch."""

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


def _to_dev_fn(half_h2d: bool):
    if half_h2d:
        from half_ops import to_device_rec_half

        return to_device_rec_half
    return _to_device_rec


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
    prefetch_depth: int = 1,
) -> dict[str, Any]:
    """
    GIVEN pinned top-k cache records on CUDA
    WHEN H2D+expand of steps ahead overlaps compute
    THEN return train ckpt and ms/step (depth 1 = PRE; depth 2 = PRE2).
    """
    if device.type != "cuda":
        raise ValueError("train_topk_prefetch requires CUDA")
    if not records:
        raise ValueError("records must be non-empty")
    if prefetch_depth not in (1, 2):
        raise ValueError("prefetch_depth must be 1 or 2")
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    student = build_fn(vocab_size).to(device)
    student.train()
    if fused_adam:
        opt = torch.optim.AdamW(student.parameters(), lr=lr, fused=True)
    else:
        opt = torch.optim.AdamW(student.parameters(), lr=lr)
    recs = pin_records(records)
    to_dev = _to_dev_fn(half_h2d)
    copy_stream = torch.cuda.Stream()
    losses: list[float] = []
    t0 = time.perf_counter()
    n = len(recs)

    def load_idx(idx: int):
        with torch.cuda.stream(copy_stream):
            return to_dev(
                recs[idx], device=device, vocab_size=vocab_size, non_blocking=True
            )

    with torch.cuda.stream(copy_stream):
        cur = to_dev(
            recs[0], device=device, vocab_size=vocab_size, non_blocking=True
        )
    torch.cuda.current_stream().wait_stream(copy_stream)
    ahead: list = []
    for j in range(1, min(prefetch_depth + 1, n)):
        ahead.append(load_idx(j))
    for i in range(n):
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
        if ahead:
            torch.cuda.current_stream().wait_stream(copy_stream)
            cur = ahead.pop(0)
            nxt = i + 1 + prefetch_depth
            if nxt < n:
                ahead.append(load_idx(nxt))
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
        "prefetch_depth": int(prefetch_depth),
        "half_h2d": bool(half_h2d),
        "fused_adam": bool(fused_adam),
    }
