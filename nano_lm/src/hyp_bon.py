"""H-BON: distill student toward teacher-scored Best-of-N winners."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from decode_ar import sample_next_batch
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_ce import ce_loss


def _bon_winner_ids(
    teacher_model,
    prompt_ids: torch.Tensor,
    *,
    n: int,
    max_new: int,
    temperature: float,
    top_p: float,
    device: torch.device,
) -> torch.Tensor:
    """Return full sequence ids [1, T] of best-of-N under teacher logprob."""
    ids = prompt_ids.repeat(n, 1)
    lps = torch.zeros(n, max_new, device=device)
    for step in range(max_new):
        tok, lp, _ = sample_next_batch(
            teacher_model, ids, temperature=temperature, top_p=top_p
        )
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
    means = lps.mean(dim=1)
    best = int(torch.argmax(means).item())
    return ids[best : best + 1]


def run_h_bon(
    *,
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    steps: int,
    bon_n: int,
    max_new: int,
    seq_prompt: int,
    lr: float,
    seed: int,
    temperature: float,
    top_p: float,
    out_path: Path,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = build_student(len(tok)).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    # fixed short prompts from tokenizer bos-ish noise
    losses: list[float] = []
    for step in range(steps):
        # synthetic prompt: random short context from vocab
        prompt = torch.randint(
            0, min(1000, len(tok)), (1, seq_prompt), device=device
        )
        with torch.no_grad():
            winner = _bon_winner_ids(
                teacher.model,
                prompt,
                n=bon_n,
                max_new=max_new,
                temperature=temperature,
                top_p=top_p,
                device=device,
            )
        opt.zero_grad(set_to_none=True)
        logits = student(winner).logits
        loss = ce_loss(logits, winner)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-BON",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
