"""KD train step under CUDA autocast + GradScaler (H-AMP train path)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from amp_ops import resolve_amp_dtype
from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def train_kd_amp(
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
    amp_kind: str = "bf16",
) -> dict[str, Any]:
    """
    GIVEN KD hyperparams and amp kind
    WHEN training
    THEN save ckpt trained under autocast; return meta.
    """
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    dtype = resolve_amp_dtype(amp_kind, device)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = build_student(len(tok)).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    use_scaler = device.type == "cuda" and dtype == torch.float16
    scaler = torch.amp.GradScaler("cuda", enabled=use_scaler)
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
        with torch.autocast(
            device_type=device.type, dtype=dtype, enabled=device.type == "cuda"
        ):
            s_logits = student(ids).logits
            loss = kd_loss(
                s_logits, t_logits, ids, temperature=temperature, alpha=alpha
            )
        if use_scaler:
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
        else:
            loss.backward()
            opt.step()
        losses.append(float(loss.detach().float().item()))
        step += 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed, "amp": amp_kind}, out_path)
    return {
        "hypothesis": "H-AMP",
        "amp_kind": amp_kind,
        "dtype": str(dtype),
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
