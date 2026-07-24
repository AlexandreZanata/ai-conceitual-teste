"""H-STEP: CURL length curriculum + early-stop on val teacher_lp plateau."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import torch

from cur_ops import N_STAGES, cur_seq_len
from data_tiny import load_tokenizer
from hyp_cur import _make_data, _next_batch
from load_model import load_causal_lm
from step_ops import improved, should_stop
from step_val import val_teacher_lp
from student_model import build_student, count_params
from train_kd import kd_loss


def _maybe_val(
    *,
    step: int,
    steps: int,
    eval_every: int,
    student,
    teacher,
    val_prompts: Path,
    max_new_val: int,
    seed: int,
    best_lp: float,
    best_state: dict | None,
    bad_streak: int,
    min_delta: float,
) -> tuple[float, dict | None, int, float | None]:
    if (step + 1) % eval_every != 0 and step + 1 != steps:
        return best_lp, best_state, bad_streak, None
    lp = val_teacher_lp(
        student,
        teacher,
        prompts_path=val_prompts,
        max_new_tokens=max_new_val,
        seed=seed + 1000 + step,
    )
    if improved(lp, best_lp, min_delta=min_delta):
        return lp, {k: v.detach().cpu().clone() for k, v in student.state_dict().items()}, 0, lp
    return best_lp, best_state, bad_streak + 1, lp


def run_h_step(
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
    val_prompts: Path,
    max_new_val: int,
    eval_every: int = 5,
    patience: int = 2,
    min_delta: float = 0.01,
    seq_lo: int = 6,
    n_stages: int = N_STAGES,
    build_fn: Callable[[int], object] = build_student,
    hypothesis: str = "H-STEP",
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
    val_lps: list[float] = []
    best_lp = float("-inf")
    best_state: dict | None = None
    bad_streak = 0
    cur = cur_seq_len(0, steps, seq_lo=seq_lo, seq_hi=seq_len, n_stages=n_stages)
    data = _make_data(tok, cache_dir, max_examples, cur, batch_size, device)
    steps_run = 0
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
        loss = kd_loss(
            student(ids).logits, t_logits, ids, temperature=temperature, alpha=alpha
        )
        loss.backward()
        opt.step()
        losses.append(float(loss.item()))
        steps_run = step + 1
        best_lp, best_state, bad_streak, vlp = _maybe_val(
            step=step,
            steps=steps,
            eval_every=eval_every,
            student=student,
            teacher=teacher,
            val_prompts=val_prompts,
            max_new_val=max_new_val,
            seed=seed,
            best_lp=best_lp,
            best_state=best_state,
            bad_streak=bad_streak,
            min_delta=min_delta,
        )
        if vlp is not None:
            val_lps.append(float(vlp))
        if should_stop(bad_streak, patience=patience):
            break
        if device.type == "cuda" and steps_run % 10 == 0:
            torch.cuda.empty_cache()
    if best_state is not None:
        student.load_state_dict(best_state)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"model": student.state_dict(), "seed": seed, "hypothesis": hypothesis},
        out_path,
    )
    return {
        "hypothesis": hypothesis,
        "params": count_params(student),
        "steps": int(steps),
        "steps_run": int(steps_run),
        "seq_lo": int(seq_lo),
        "eval_every": int(eval_every),
        "patience": int(patience),
        "best_val_lp": float(best_lp),
        "n_val": len(val_lps),
        "mean_loss": sum(losses) / max(len(losses), 1),
        "out_path": str(out_path),
    }
