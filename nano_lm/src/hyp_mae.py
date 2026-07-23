"""H-MAE: distill student on lookahead-MAE committed sequences (teacher)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from decode_mae import decode_mae
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_ce import ce_loss


def run_h_mae(
    *,
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    steps: int,
    k: int,
    block: int,
    horizon: int,
    max_new: int,
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
    prompts = [
        "Once upon a time there was",
        "One day, a boy found a key",
    ]
    losses: list[float] = []
    for step in range(steps):
        text = prompts[step % len(prompts)]
        with torch.no_grad():
            result = decode_mae(
                teacher.model,
                tok,
                text,
                k=k,
                block=block,
                horizon=horizon,
                max_new_tokens=max_new,
                temperature=temperature,
                top_p=top_p,
                seed=seed + step,
                device=device,
            )
        prompt_ids = tok.encode(text, return_tensors="pt").to(device)
        cont = torch.tensor([list(result.token_ids)], device=device)
        full = torch.cat([prompt_ids, cont], dim=1)
        opt.zero_grad(set_to_none=True)
        loss = ce_loss(student(full).logits, full)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-MAE",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
