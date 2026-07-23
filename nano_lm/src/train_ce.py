"""Train student with causal LM cross-entropy (baseline B1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from data_tiny import iter_token_batches, load_tokenizer
from student_model import build_student, count_params


def ce_loss(logits: torch.Tensor, ids: torch.Tensor) -> torch.Tensor:
    """Shifted next-token CE."""
    shift_logits = logits[:, :-1, :].contiguous()
    shift_labels = ids[:, 1:].contiguous()
    return F.cross_entropy(
        shift_logits.view(-1, shift_logits.size(-1)),
        shift_labels.view(-1),
    )


def train_ce(
    *,
    steps: int,
    batch_size: int,
    seq_len: int,
    max_examples: int,
    lr: float,
    seed: int,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    out_path: Path,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
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
        logits = student(ids).logits
        loss = ce_loss(logits, ids)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        step += 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "baseline": "B1",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
