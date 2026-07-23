"""H-ENT: dual heads + agreement reward; kill if heads collapse."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import yaml

from data_tiny import iter_token_batches, load_tokenizer
from decode_ar import decode_ar
from dual_student import DualHeadStudent, build_dual_student
from ent_ops import agreement_loss, head_tv_distance, heads_collapsed
from eval_student import teacher_mean_logprob
from load_model import load_causal_lm
from student_model import count_params
from train_kd import kd_loss


def run_h_ent(
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
    agree_weight: float,
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
        loss = _ent_loss(la, lb, t_logits, ids, temperature, alpha, agree_weight)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        tvs.append(head_tv_distance(la.detach(), lb.detach()))
        step += 1
        if device.type == "cuda" and step % 10 == 0:
            torch.cuda.empty_cache()
    mean_tv = sum(tvs) / max(len(tvs), 1)
    collapsed = heads_collapsed(mean_tv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed, "dual": True}, out_path)
    return {
        "hypothesis": "H-ENT",
        "params": count_params(student),
        "steps": steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "mean_tv": mean_tv,
        "heads_collapsed": collapsed,
        "agree_weight": agree_weight,
        "out_path": str(out_path),
    }


def _ent_loss(
    la: torch.Tensor,
    lb: torch.Tensor,
    t_logits: torch.Tensor,
    ids: torch.Tensor,
    temperature: float,
    alpha: float,
    agree_weight: float,
) -> torch.Tensor:
    kd_a = kd_loss(la, t_logits, ids, temperature=temperature, alpha=alpha)
    kd_b = kd_loss(lb, t_logits, ids, temperature=temperature, alpha=alpha)
    return 0.5 * (kd_a + kd_b) + agree_weight * agreement_loss(la, lb)


def load_dual_ckpt(path: Path, vocab: int, device: torch.device) -> DualHeadStudent:
    dual = build_dual_student(vocab).to(device)
    blob = torch.load(path, map_location=device, weights_only=True)
    dual.load_state_dict(blob["model"])
    dual.eval()
    return dual


def eval_dual_vs_teacher(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new_tokens: int,
    seed: int,
    temperature: float,
    top_p: float,
) -> dict[str, Any]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    tok = teacher.tokenizer
    dual = load_dual_ckpt(student_ckpt, len(tok), teacher.device)
    with prompts_path.open(encoding="utf-8") as f:
        prompts = yaml.safe_load(f)["prompts"]
    scores: list[float] = []
    walls: list[float] = []
    for i, p in enumerate(prompts):
        result = decode_ar(
            dual,
            tok,
            p["text"],
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            seed=seed + i,
            device=teacher.device,
        )
        prompt_ids = tok.encode(p["text"], return_tensors="pt")
        scores.append(
            teacher_mean_logprob(teacher, prompt_ids, list(result.token_ids))
        )
        walls.append(result.wall_ms)
    return {
        "label": student_ckpt.stem,
        "teacher_mean_logprob": sum(scores) / len(scores),
        "mean_wall_ms": sum(walls) / len(walls),
        "n_prompts": len(prompts),
        "seed": seed,
    }
