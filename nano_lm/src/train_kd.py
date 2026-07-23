"""Knowledge distillation: KL(student ‖ teacher) soft targets (baseline B2)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_ce import ce_loss


def kd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    ids: torch.Tensor,
    *,
    temperature: float,
    alpha: float,
) -> torch.Tensor:
    """alpha * CE + (1-alpha) * T^2 * KL(student ‖ teacher) on shifted tokens."""
    t = max(temperature, 1e-6)
    s = student_logits[:, :-1, :].float() / t
    tea = teacher_logits[:, :-1, :].float() / t
    log_p = F.log_softmax(s, dim=-1)
    q = F.softmax(tea, dim=-1)
    kl = F.kl_div(log_p, q, reduction="batchmean") * (t * t)
    return alpha * ce_loss(student_logits, ids) + (1.0 - alpha) * kl


def train_kd(
    *,
    teacher_id: str,
    steps: int,
    batch_size: int,
    seq_len: int,
    max_examples: int,
    lr: float,
    seed: int,
    temperature: float,
    alpha: float,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    out_path: Path,
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
        opt.zero_grad(set_to_none=True)
        with torch.no_grad():
            t_logits = teacher.model(ids).logits
        s_logits = student(ids).logits
        loss = kd_loss(
            s_logits, t_logits, ids, temperature=temperature, alpha=alpha
        )
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "baseline": "B2",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
