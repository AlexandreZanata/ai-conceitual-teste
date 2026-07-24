"""Short KD recovery after magnitude prune (masks enforced each step)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from prun_mask import apply_masks, density_of, magnitude_prune, sparsity_of
from student_model import count_params
from train_kd import kd_loss


def recover_pruned_kd(
    *,
    student: object,
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
    sparsity: float,
    out_path: Path,
) -> dict[str, Any]:
    """
    GIVEN a loaded STAG student
    WHEN magnitude-pruning then KD recovery
    THEN save pruned+recovered ckpt; return sparsity meta.
    """
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    masks = magnitude_prune(student, sparsity=sparsity)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
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
    for step in range(steps):
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
        apply_masks(student, masks)
        losses.append(float(loss.item()))
        del step
    student.eval()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": student.state_dict(),
            "seed": seed,
            "hypothesis": "H-PRUN",
            "sparsity_target": sparsity,
            "sparsity": sparsity_of(student),
        },
        out_path,
    )
    return {
        "hypothesis": "H-PRUN",
        "params": count_params(student),
        "steps": steps,
        "sparsity_target": sparsity,
        "sparsity": sparsity_of(student),
        "density": density_of(student),
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
