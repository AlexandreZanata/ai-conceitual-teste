"""H-CUR: KD with linear seq_len curriculum (short → full)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from cur_ops import DEFAULT_SEQ_LO, N_STAGES, cur_seq_len
from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def _make_data(tok, cache_dir, max_examples, seq_len, batch_size, device):
    return iter_token_batches(
        tok,
        cache_dir=cache_dir,
        max_examples=max_examples,
        seq_len=seq_len,
        batch_size=batch_size,
        device=device,
    )


def _next_batch(data, tok, cache_dir, max_examples, seq_len, batch_size, device):
    try:
        return next(data), data
    except StopIteration:
        data = _make_data(tok, cache_dir, max_examples, seq_len, batch_size, device)
        return next(data), data


def run_h_cur(
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
    seq_lo: int = DEFAULT_SEQ_LO,
    n_stages: int = N_STAGES,
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
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    losses: list[float] = []
    lens: list[int] = []
    cur = cur_seq_len(
        0, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages
    )
    data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
    for step in range(steps):
        want = cur_seq_len(
            step, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages
        )
        if want != cur:
            cur = want
            data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
        ids, data = _next_batch(
            data, tok, cache_dir, max_examples, cur, batch_size, device
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
        lens.append(cur)
        if device.type == "cuda" and (step + 1) % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-CUR",
        "params": count_params(student),
        "steps": steps,
        "n_stages": int(n_stages),
        "seq_lo": int(seq_lo),
        "seq_hi": int(seq_len),
        "mean_seq_len": sum(lens) / max(len(lens), 1),
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
