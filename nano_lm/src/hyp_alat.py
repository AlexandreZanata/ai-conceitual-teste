"""H-ALAT: CURL length curriculum with scheduled KD α / temperature."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import torch

from alat_ops import alat_alpha, alat_temp, curd_stage
from cur_ops import N_STAGES, cur_seq_len
from data_tiny import load_tokenizer
from hyp_cur import _make_data, _next_batch
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def run_h_alat(
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
    out_path: Path,
    seq_lo: int = 6,
    n_stages: int = N_STAGES,
    build_fn: Callable[[int], object] = build_student,
    hypothesis: str = "H-ALAT",
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = build_fn(len(tok)).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    losses: list[float] = []
    alphas: list[float] = []
    temps: list[float] = []
    cur = cur_seq_len(0, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages)
    data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
    for step in range(steps):
        want = cur_seq_len(
            step, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages
        )
        if want != cur:
            cur = want
            data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
        stage = curd_stage(step, steps, n_stages=n_stages)
        alpha = alat_alpha(stage, n_stages=n_stages)
        temperature = alat_temp(stage, n_stages=n_stages)
        ids, data = _next_batch(
            data, tok, cache_dir, max_examples, cur, batch_size, device
        )
        opt.zero_grad(set_to_none=True)
        with torch.no_grad():
            t_logits = teacher.model(ids).logits
        loss = kd_loss(
            student(ids).logits,
            t_logits,
            ids,
            temperature=temperature,
            alpha=alpha,
        )
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        alphas.append(alpha)
        temps.append(temperature)
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
        "seq_lo": int(seq_lo),
        "n_stages": int(n_stages),
        "mean_alpha": sum(alphas) / max(len(alphas), 1),
        "mean_temp": sum(temps) / max(len(temps), 1),
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
