"""H-ZERR train: tiny CE steps on error-bank Q→A only (no TinyStories/MIXD)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from student_model import count_params
from train_ce import ce_loss
from zerr_ops import DEFAULT_STEPS, HYPOTHESIS, format_qa


def _encode_pair(tok: Any, question: str, gold: str, device: torch.device) -> torch.Tensor:
    text = format_qa(question, gold)
    ids = tok.encode(text, return_tensors="pt")
    return ids.to(device)


def train_zerr(
    *,
    student: Any,
    tok: Any,
    pairs: list[tuple[str, str]],
    device: torch.device,
    steps: int = DEFAULT_STEPS,
    lr: float = 3e-4,
    seed: int = 0,
    out_path: Path,
) -> dict[str, Any]:
    """
    GIVEN loaded ≤5M student + bank pairs
    WHEN running tiny AdamW CE steps cycling Q→A texts
    THEN save ckpt and return train meta (no MIXD / no teacher KD).
    """
    if not pairs:
        raise ValueError("train_zerr requires non-empty pairs")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=float(lr))
    losses: list[float] = []
    n = len(pairs)
    for step in range(int(steps)):
        q, g = pairs[step % n]
        ids = _encode_pair(tok, q, g, device)
        if int(ids.shape[1]) < 2:
            continue
        opt.zero_grad(set_to_none=True)
        logits = student(ids).logits
        loss = ce_loss(logits, ids)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model": student.state_dict(),
            "seed": int(seed),
            "hypothesis": HYPOTHESIS,
            "n_pairs": n,
            "steps": int(steps),
        },
        out_path,
    )
    return {
        "hypothesis": HYPOTHESIS,
        "params": count_params(student),
        "steps": int(steps),
        "n_pairs": n,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "final_loss": losses[-1] if losses else None,
        "out_path": str(out_path),
        "lr": float(lr),
        "seed": int(seed),
    }
