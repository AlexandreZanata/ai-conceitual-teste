"""H-LOT: KD with magnitude lottery ticket (warmup → prune → rewind → retrain)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from lot_ops import (
    apply_weight_masks,
    build_magnitude_masks,
    collect_linear_inits,
    mask_keep_frac,
    rewind_linears,
)
from student_model import build_student, count_params
from train_kd import kd_loss


def _next_batch(data, tok, cache_dir, max_examples, seq_len, batch_size, device):
    try:
        return next(data), data
    except StopIteration:
        data = iter_token_batches(
            tok,
            cache_dir=cache_dir,
            max_examples=max_examples,
            seq_len=seq_len,
            batch_size=batch_size,
            device=device,
        )
        return next(data), data


def run_h_lot(
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
    keep_frac: float = 0.3,
    warmup_frac: float = 0.25,
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
    inits = collect_linear_inits(student)
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
    warmup = max(1, int(steps * warmup_frac))
    masks: dict[str, torch.Tensor] | None = None
    step = 0
    while step < steps:
        ids, data = _next_batch(
            data, tok, cache_dir, max_examples, seq_len, batch_size, device
        )
        opt.zero_grad(set_to_none=True)
        with torch.no_grad():
            t_logits = teacher.model(ids).logits
        loss = kd_loss(
            student(ids).logits, t_logits, ids, temperature=temperature, alpha=alpha
        )
        loss.backward()
        opt.step()
        if step + 1 == warmup:
            masks = build_magnitude_masks(student, keep_frac)
            rewind_linears(student, inits, masks)
            opt = torch.optim.AdamW(student.parameters(), lr=lr)
        elif masks is not None:
            apply_weight_masks(student, masks)
        losses.append(float(loss.item()))
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    if masks is None:
        masks = build_magnitude_masks(student, keep_frac)
        rewind_linears(student, inits, masks)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-LOT",
        "params": count_params(student),
        "steps": steps,
        "warmup": warmup,
        "keep_frac_target": keep_frac,
        "keep_frac_actual": mask_keep_frac(masks),
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
