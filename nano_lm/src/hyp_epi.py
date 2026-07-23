"""H-EPI: KD with context-dependent LR and embed grad mask."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from epi_ops import (
    context_lr_scale,
    mean_token_entropy,
    should_mask_embeds,
    zero_embed_grads,
)
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def run_h_epi(
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
    out_path: Path,
    ent_lo: float = 1.0,
    ent_hi: float = 6.0,
    mask_threshold: float = 3.0,
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
    mask_hits = 0
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
        with torch.no_grad():
            t_logits = teacher.model(ids).logits
            ent = mean_token_entropy(t_logits)
        scale = context_lr_scale(ent, ent_lo=ent_lo, ent_hi=ent_hi)
        cur_lr = lr * scale
        for g in opt.param_groups:
            g["lr"] = cur_lr
        opt.zero_grad(set_to_none=True)
        s_logits = student(ids).logits
        loss = kd_loss(
            s_logits, t_logits, ids, temperature=temperature, alpha=alpha
        )
        loss.backward()
        if should_mask_embeds(ent, threshold=mask_threshold):
            zero_embed_grads(student)
            mask_hits += 1
        opt.step()
        losses.append(float(loss.item()))
        lr_hist.append(cur_lr)
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-EPI",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "mean_lr": sum(lr_hist) / max(len(lr_hist), 1),
        "mask_rate": mask_hits / max(steps, 1),
        "lr_hist": lr_hist,
        "out_path": str(out_path),
    }
