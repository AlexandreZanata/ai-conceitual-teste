"""H-ADV: KD + weak discriminator; teacher remains claim judge."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from adv_ops import (
    TOP_K,
    WeakDisc,
    disc_bce,
    mode_collapsed,
    pred_entropy,
    soft_topk_feats,
)
from data_tiny import iter_token_batches, load_tokenizer
from load_model import load_causal_lm
from student_model import build_student, count_params
from train_kd import kd_loss


def _next_batch(data, tok, cache_dir, max_examples, seq_len, batch_size, device):
    try:
        return next(data), data
    except StopIteration:
        data = iter_token_batches(
            tok,
            cache_dir=cache_dir,
            max_examples=max_examples,
            seq_len=seq_len,
            batch_size=batch_size,
            device=device,
        )
        return next(data), data


def _adv_step(teacher, student, disc, opt_d, opt_s, ids, *, t, a, w):
    with torch.no_grad():
        t_logits = teacher.model(ids).logits
    s_logits = student(ids).logits
    opt_d.zero_grad(set_to_none=True)
    real_f = soft_topk_feats(t_logits.detach())
    fake_f = soft_topk_feats(s_logits.detach())
    d_loss = disc_bce(disc(real_f), real=True) + disc_bce(disc(fake_f), real=False)
    d_loss.backward()
    opt_d.step()
    opt_s.zero_grad(set_to_none=True)
    kd = kd_loss(s_logits, t_logits, ids, temperature=t, alpha=a)
    fool = disc_bce(disc(soft_topk_feats(s_logits)), real=True)
    loss = kd + float(w) * fool
    loss.backward()
    opt_s.step()
    return float(loss.item()), pred_entropy(s_logits.detach())


def run_h_adv(
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
    adv_weight: float = 0.1,
    disc_lr: float = 1e-3,
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
    disc = WeakDisc(TOP_K).to(device)
    opt_s = torch.optim.AdamW(student.parameters(), lr=lr)
    opt_d = torch.optim.AdamW(disc.parameters(), lr=disc_lr)
    losses: list[float] = []
    ents: list[float] = []
    data = iter_token_batches(
        tok,
        cache_dir=cache_dir,
        max_examples=max_examples,
        seq_len=seq_len,
        batch_size=batch_size,
        device=device,
    )
    for step in range(steps):
        ids, data = _next_batch(
            data, tok, cache_dir, max_examples, seq_len, batch_size, device
        )
        loss, ent = _adv_step(
            teacher,
            student,
            disc,
            opt_d,
            opt_s,
            ids,
            t=temperature,
            a=alpha,
            w=adv_weight,
        )
        losses.append(loss)
        ents.append(ent)
        if device.type == "cuda" and (step + 1) % 10 == 0:
            torch.cuda.empty_cache()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    collapsed = mode_collapsed(ents[0], ents[-1]) if ents else True
    return {
        "hypothesis": "H-ADV",
        "params": count_params(student),
        "steps": steps,
        "adv_weight": adv_weight,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "entropy_start": ents[0] if ents else 0.0,
        "entropy_end": ents[-1] if ents else 0.0,
        "mode_collapsed": collapsed,
        "out_path": str(out_path),
    }
