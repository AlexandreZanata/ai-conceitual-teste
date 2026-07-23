"""H-DIF: absorb-mask diffusion train + iterative decode eval."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
import yaml

from data_tiny import iter_token_batches, load_tokenizer
from decode_dif import decode_dif
from dif_ops import corrupt_tokens
from eval_student import load_student_ckpt, teacher_mean_logprob
from load_model import load_causal_lm
from student_model import build_student, count_params


def _peak_vram_mib(device: torch.device) -> float:
    if device.type != "cuda":
        return 0.0
    return float(torch.cuda.max_memory_allocated(device)) / (1024.0 * 1024.0)


def _dif_ce(logits: torch.Tensor, clean: torch.Tensor, noise: torch.Tensor) -> torch.Tensor:
    """CE on corrupted positions only."""
    if not bool(noise.any()):
        return logits.sum() * 0.0
    flat_logits = logits.reshape(-1, logits.shape[-1])
    flat_tgt = clean.reshape(-1)
    flat_noise = noise.reshape(-1)
    return F.cross_entropy(flat_logits[flat_noise], flat_tgt[flat_noise])


def run_h_dif(
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
    dif_steps: int = 4,
    prompts_path: Path | None = None,
    max_new_eval: int = 32,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
        torch.cuda.reset_peak_memory_stats(device)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    mask_id = int(tok.eos_token_id)
    student = build_student(len(tok)).to(device)
    student.train()
    opt = torch.optim.AdamW(student.parameters(), lr=lr)
    losses: list[float] = []
    gen = torch.Generator()
    gen.manual_seed(seed)
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
        rate = float(torch.rand((), generator=gen).item())
        noisy, noise = corrupt_tokens(ids, rate=rate, mask_id=mask_id, generator=gen)
        opt.zero_grad(set_to_none=True)
        logits = student(noisy).logits
        loss = _dif_ce(logits, ids, noise)
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        step += 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": student.state_dict(), "seed": seed}, out_path)
    peak = _peak_vram_mib(device)
    eval_lp, eval_wall = 0.0, 0.0
    if prompts_path is not None:
        teacher = load_causal_lm(
            teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
        )
        student_e = load_student_ckpt(out_path, teacher.tokenizer, teacher.device)
        prompts = [
            p["text"]
            for p in yaml.safe_load(prompts_path.read_text(encoding="utf-8"))["prompts"]
        ]
        scores: list[float] = []
        walls: list[float] = []
        t0 = time.perf_counter()
        for i, text in enumerate(prompts):
            result = decode_dif(
                student_e,
                teacher.tokenizer,
                text,
                max_new_tokens=max_new_eval,
                dif_steps=dif_steps,
                temperature=0.8,
                top_p=0.9,
                seed=seed + i,
                device=teacher.device,
                mask_id=mask_id,
            )
            walls.append(float(result.wall_ms))
            ids = teacher.tokenizer.encode(text, return_tensors="pt")
            scores.append(
                teacher_mean_logprob(teacher, ids, list(result.token_ids))
            )
        eval_lp = sum(scores) / len(scores)
        eval_wall = sum(walls) / len(walls)
        peak = max(peak, _peak_vram_mib(device))
        _ = time.perf_counter() - t0
    return {
        "hypothesis": "H-DIF",
        "params": count_params(student),
        "steps": steps,
        "dif_steps": dif_steps,
        "mean_loss": sum(losses) / max(len(losses), 1),
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "peak_vram_mib": peak,
        "out_path": str(out_path),
    }
