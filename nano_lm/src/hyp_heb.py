"""H-HEB: KD + local Hebbian update on last MLP c_fc."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from heb_ops import apply_hebbian, diverged
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def _heb_linear(student: Any) -> torch.nn.Linear:
    return student.transformer.h[-1].mlp.c_fc


def run_h_heb(
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
    heb_eta: float = 1e-4,
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
    layer = _heb_linear(student)
    cache: dict[str, torch.Tensor] = {}

    def _hook(_mod, inputs, output):
        cache["pre"] = inputs[0].detach()
        cache["post"] = output.detach()

    handle = layer.register_forward_hook(_hook)
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
    try:
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
            s_logits = student(ids).logits
            loss = kd_loss(
                s_logits, t_logits, ids, temperature=temperature, alpha=alpha
            )
            loss.backward()
            opt.step()
            if "pre" in cache and "post" in cache:
                apply_hebbian(
                    layer.weight, cache["pre"], cache["post"], eta=heb_eta
                )
            losses.append(float(loss.item()))
            step += 1
            if device.type == "cuda" and step % 10 == 0:
                torch.cuda.empty_cache()
    finally:
        handle.remove()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    bad = diverged(losses)
    return {
        "hypothesis": "H-HEB",
        "params": count_params(student),
        "steps": steps,
        "heb_eta": heb_eta,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "diverged": bad,
        "out_path": str(out_path),
    }
