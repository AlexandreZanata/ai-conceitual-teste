"""Scheduled KD: cosine LR (control) vs anneal LR+temp (H-ANN)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from schedules import schedule_pair
from student_model import build_student, count_params
from train_kd import kd_loss


def train_kd_scheduled(
    *,
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    steps: int,
    batch_size: int,
    seq_len: int,
    max_examples: int,
    lr: float,
    seed: int,
    temperature: float,
    alpha: float,
    schedule: str,
    out_path: Path,
    lr_end_ratio: float = 0.1,
    temp_end: float = 1.0,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = build_student(len(tok)).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    losses: list[float] = []
    lr_hist: list[float] = []
    temp_hist: list[float] = []
    data = iter_token_batches(
        tok,
        cache_dir=cache_dir,
        max_examples=max_examples,
        seq_len=seq_len,
        batch_size=batch_size,
        device=device,
    )
    step = 0
    while step < steps:
        try:
            ids = next(data)
        except StopIteration:
            data = iter_token_batches(
                tok,
                cache_dir=cache_dir,
                max_examples=max_examples,
                seq_len=seq_len,
                batch_size=batch_size,
                device=device,
            )
            ids = next(data)
        cur_lr, cur_temp = schedule_pair(
            schedule,
            step,
            steps,
            lr_start=lr,
            lr_end=lr * lr_end_ratio,
            temp_start=temperature,
            temp_end=temp_end,
        )
        for g in opt.param_groups:
            g["lr"] = cur_lr
        opt.zero_grad(set_to_none=True)
        with torch.no_grad():
            t_logits = teacher.model(ids).logits
        loss = kd_loss(
            student(ids).logits,
            t_logits,
            ids,
            temperature=cur_temp,
            alpha=alpha,
        )
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        lr_hist.append(cur_lr)
        temp_hist.append(cur_temp)
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-ANN" if schedule == "anneal" else "KD-cos",
        "schedule": schedule,
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "lr_hist": lr_hist,
        "temp_hist": temp_hist,
        "out_path": str(out_path),
    }


def run_h_ann(**kwargs: Any) -> dict[str, Any]:
    return train_kd_scheduled(schedule="anneal", **kwargs)


def run_kd_cosine(**kwargs: Any) -> dict[str, Any]:
    return train_kd_scheduled(schedule="cosine", **kwargs)
