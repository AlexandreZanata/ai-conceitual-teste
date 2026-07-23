"""H-HOP: KD with continuous Hopfield prior on hidden states."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from hop_ops import hopfield_retrieve, mix_hidden, push_patterns
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def _hop_logits(
    student: Any,
    ids: torch.Tensor,
    bank: torch.Tensor,
    *,
    beta: float,
    alpha: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    out = student(ids, output_hidden_states=True)
    hidden = out.hidden_states[-1]
    retrieved = hopfield_retrieve(hidden, bank, beta=beta)
    mixed = mix_hidden(hidden, retrieved, alpha=alpha)
    return student.lm_head(mixed), hidden


def run_h_hop(
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
    alpha_kd: float,
    out_path: Path,
    mem_size: int = 32,
    hop_beta: float = 8.0,
    hop_alpha: float = 0.25,
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
    d_model = int(student.config.hidden_size)
    bank = torch.randn(mem_size, d_model, device=device) * 0.02
    cursor = 0
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
        with torch.no_grad():
            t_logits = teacher.model(ids).logits
        s_logits, hidden = _hop_logits(
            student, ids, bank, beta=hop_beta, alpha=hop_alpha
        )
        loss = kd_loss(
            s_logits, t_logits, ids, temperature=temperature, alpha=alpha_kd
        )
        loss.backward()
        opt.step()
        flat = hidden.detach().mean(dim=1)
        cursor = push_patterns(bank, flat, cursor=cursor)
        losses.append(float(loss.item()))
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    return {
        "hypothesis": "H-HOP",
        "params": count_params(student),
        "steps": steps,
        "mem_size": mem_size,
        "hop_beta": hop_beta,
        "hop_alpha": hop_alpha,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
