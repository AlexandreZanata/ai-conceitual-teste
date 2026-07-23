"""H-DEB: dual students; teacher picks; both distill (+ peer pull)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from deb_ops import peer_kl, soft_kl, teacher_pick
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


def _deb_step(teacher, pair, opts, ids, *, t, a, peer_w):
    s0, s1 = pair
    with torch.no_grad():
        t_logits = teacher.model(ids).logits
    z0, z1 = s0(ids).logits, s1(ids).logits
    pick = teacher_pick(
        float(soft_kl(z0.detach(), t_logits, temperature=t).item()),
        float(soft_kl(z1.detach(), t_logits, temperature=t).item()),
    )
    win_z = (z0 if pick == 0 else z1).detach()
    losses: list[float] = []
    for i, (stu, opt, z) in enumerate(((s0, opts[0], z0), (s1, opts[1], z1))):
        opt.zero_grad(set_to_none=True)
        loss = kd_loss(z, t_logits, ids, temperature=t, alpha=a)
        if i != pick:
            loss = loss + float(peer_w) * peer_kl(z, win_z, temperature=t)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
    return pick, sum(losses) / 2.0


def run_h_deb(
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
    peer_weight: float = 0.25,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    s0 = build_student(len(tok)).to(device)
    torch.manual_seed(seed + 1000)
    s1 = build_student(len(tok)).to(device)
    s0.train()
    s1.train()
    opts = (
        torch.optim.AdamW(s0.parameters(), lr=lr),
        torch.optim.AdamW(s1.parameters(), lr=lr),
    )
    losses: list[float] = []
    picks: list[int] = []
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
        pick, loss = _deb_step(
            teacher,
            (s0, s1),
            opts,
            ids,
            t=temperature,
            a=alpha,
            peer_w=peer_weight,
        )
        picks.append(pick)
        losses.append(loss)
        if device.type == "cuda" and (step + 1) % 10 == 0:
            torch.cuda.empty_cache()
    winner = s0 if (picks[-1] if picks else 0) == 0 else s1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": winner.state_dict(), "seed": seed}, out_path)
    n0 = sum(1 for p in picks if p == 0)
    return {
        "hypothesis": "H-DEB",
        "params": count_params(s0),
        "steps": steps,
        "peer_weight": peer_weight,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "pick_a_rate": n0 / max(len(picks), 1),
        "last_pick": picks[-1] if picks else 0,
        "out_path": str(out_path),
    }
