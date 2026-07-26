"""H-ZPREF train: rank loss prefer gold≻raw (no MIXD / no TinyStories)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from student_model import count_params
from train_ce import ce_loss
from zpref_ops import BETA, DEFAULT_STEPS, HYPOTHESIS, format_qa


def _encode(tok: Any, question: str, answer: str, device: torch.device) -> torch.Tensor:
    ids = tok.encode(format_qa(question, answer), return_tensors="pt")
    return ids.to(device)


def _seq_nll(student: Any, ids: torch.Tensor) -> torch.Tensor:
    """Mean next-token NLL for a packed Q→A sequence."""
    logits = student(ids).logits
    return ce_loss(logits, ids)


def train_zpref(
    *,
    student: Any,
    tok: Any,
    pairs: list[tuple[str, str, str]],
    device: torch.device,
    steps: int = DEFAULT_STEPS,
    lr: float = 3e-4,
    seed: int = 0,
    out_path: Path,
    beta: float = BETA,
) -> dict[str, Any]:
    """
    GIVEN ≤5M student + (q, chosen, rejected) triples
    WHEN DPO-lite softplus(β·(nll_c − nll_r)) steps
    THEN save ckpt; prefer lower NLL on gold than on raw.
    """
    if not pairs:
        raise ValueError("train_zpref requires non-empty pairs")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=float(lr))
    losses: list[float] = []
    n = len(pairs)
    b = float(beta)
    for step in range(int(steps)):
        q, chosen, rejected = pairs[step % n]
        ids_c = _encode(tok, q, chosen, device)
        ids_r = _encode(tok, q, rejected, device)
        if int(ids_c.shape[1]) < 2 or int(ids_r.shape[1]) < 2:
            continue
        opt.zero_grad(set_to_none=True)
        nll_c = _seq_nll(student, ids_c)
        nll_r = _seq_nll(student, ids_r)
        # Prefer nll_c < nll_r ⇔ softplus(β (nll_c − nll_r)) → 0
        loss = F.softplus(b * (nll_c - nll_r))
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
        "beta": b,
    }
