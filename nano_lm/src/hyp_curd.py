"""H-CURD: KD with teacher-NLL difficulty curriculum (fixed seq_len)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import torch

from cur_ops import N_STAGES
from curd_data import (
    batch_from_pool,
    collect_chunks,
    sort_easy_first,
)
from curd_ops import curd_stage, easy_frac
from data_tiny import load_tokenizer
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def run_h_curd(
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
    n_stages: int = N_STAGES,
    build_fn: Callable[[int], object] = build_student,
    hypothesis: str = "H-CURD",
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    chunks = collect_chunks(
        tok,
        cache_dir=cache_dir,
        max_examples=max_examples,
        seq_len=seq_len,
        batch_size=batch_size,
        device=device,
    )
    ranked = sort_easy_first(teacher, chunks, device)
    student = build_fn(len(tok)).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    losses: list[float] = []
    fracs: list[float] = []
    cursor = 0
    stage = -1
    pool = ranked
    for step in range(steps):
        want = curd_stage(step, steps, n_stages=n_stages)
        if want != stage:
            stage = want
            frac = easy_frac(stage, n_stages=n_stages)
            k = max(batch_size, int(round(len(ranked) * frac)))
            pool = ranked[:k]
            cursor = 0
        ids, cursor = batch_from_pool(
            pool, start=cursor, batch_size=batch_size, device=device
        )
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
        fracs.append(easy_frac(stage, n_stages=n_stages))
        if device.type == "cuda" and (step + 1) % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"model": student.state_dict(), "seed": seed, "hypothesis": hypothesis},
        out_path,
    )
    return {
        "hypothesis": hypothesis,
        "params": count_params(student),
        "steps": steps,
        "n_stages": int(n_stages),
        "seq_len": int(seq_len),
        "curriculum": "teacher_nll",
        "mean_easy_frac": sum(fracs) / max(len(fracs), 1),
        "mean_loss": sum(losses) / max(len(losses), 1),
        "pool_size": len(ranked),
        "out_path": str(out_path),
    }
