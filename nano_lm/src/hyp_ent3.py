"""H-ENT3: dual heads; KD on mix; reward disagreement (maximize TV)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from dual_student import build_dual_student
from ent_ops import head_tv_distance
from ent3_ops import collapse_or_chaos, mix_logits, soft_tv
from hyp_ent import eval_dual_vs_teacher
from load_model import load_causal_lm
from student_model import count_params
from train_kd import kd_loss


def run_h_ent3(
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
    disagree_weight: float,
    noise_std: float,
    out_path: Path,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = build_dual_student(len(tok), noise_std=noise_std).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    losses: list[float] = []
    tvs: list[float] = []
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
        la, lb = student.forward_dual(ids)
        loss = _ent3_loss(la, lb, t_logits, ids, temperature, alpha, disagree_weight)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        tvs.append(head_tv_distance(la.detach(), lb.detach()))
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    mean_tv = sum(tvs) / max(len(tvs), 1)
    collapsed, chaos = collapse_or_chaos(mean_tv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed, "dual": True}, out_path)
    return {
        "hypothesis": "H-ENT3",
        "parents": ["H-ENT", "H-ENT2"],
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "mean_tv": mean_tv,
        "disagree_weight": disagree_weight,
        "heads_collapsed": collapsed,
        "mode_chaos": chaos,
        "out_path": str(out_path),
    }


def _ent3_loss(
    la: torch.Tensor,
    lb: torch.Tensor,
    t_logits: torch.Tensor,
    ids: torch.Tensor,
    temperature: float,
    alpha: float,
    disagree_weight: float,
) -> torch.Tensor:
    mixed = mix_logits(la, lb)
    kd = kd_loss(mixed, t_logits, ids, temperature=temperature, alpha=alpha)
    # Minimize loss ⇒ maximize soft_tv when disagree_weight > 0.
    return kd - disagree_weight * soft_tv(la, lb)


eval_ent3_vs_teacher = eval_dual_vs_teacher
