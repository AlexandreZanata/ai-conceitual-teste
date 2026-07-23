"""H-BAL / shared plastic evo: lifetime GD + selectable inherit mode."""

from __future__ import annotations

import copy
import math
import time
from pathlib import Path
from typing import Any

import torch

from baldwin_inherit import inherit_weights
from data_tiny import iter_token_batches, load_tokenizer
from hyp_sel import mutate_state
from student_model import build_student, count_params
from train_ce import ce_loss


def _lifetime_gd(
    model: Any,
    batches: list[torch.Tensor],
    *,
    steps: int,
    lr: float,
) -> float:
    """N AdamW CE steps; returns final probe fitness (−CE on batches[0])."""
    model.train()
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    n = len(batches)
    for i in range(steps):
        ids = batches[i % n]
        opt.zero_grad(set_to_none=True)
        loss = ce_loss(model(ids).logits, ids)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        return -float(ce_loss(model(batches[0]).logits, batches[0]).item())


def run_plastic_evo(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    lifetime_steps: int,
    mutate_scale: float,
    seq_len: int,
    batch_size: int,
    max_examples: int,
    lr: float,
    seed: int,
    out_path: Path,
    inherit_mode: str,
    hypothesis: str,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
    genotypes = [build_student(vocab).state_dict() for _ in range(pop_size)]
    data = list(
        iter_token_batches(
            tok,
            cache_dir=cache_dir,
            max_examples=max_examples,
            seq_len=seq_len,
            batch_size=batch_size,
            device=device,
        )
    )
    if not data:
        raise RuntimeError(f"{hypothesis}: no training batches")
    best_pheno = None
    best_fit = float("-inf")
    history: list[float] = []
    unstable = False
    t0 = time.perf_counter()
    for _gen in range(generations):
        fits, phenos = _eval_pop(
            genotypes, vocab, data, device, lifetime_steps, lr
        )
        if any(not math.isfinite(f) for f in fits):
            unstable = True
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append(fits[ranked[0]])
        if fits[ranked[0]] > best_fit and math.isfinite(fits[ranked[0]]):
            best_fit = fits[ranked[0]]
            best_pheno = phenos[ranked[0]]
        parents = ranked[: max(1, pop_size // 2)]
        genotypes = _next_gen(
            genotypes, phenos, parents, pop_size, mutate_scale, inherit_mode
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_pheno is not None
    torch.save({"model": best_pheno, "seed": seed}, out_path)
    return {
        "hypothesis": hypothesis,
        "inherit_mode": inherit_mode,
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "lifetime_steps": lifetime_steps,
        "unstable": unstable,
        "wall_s": wall_s,
        "out_path": str(out_path),
    }


def _eval_pop(
    genotypes: list,
    vocab: int,
    data: list,
    device: torch.device,
    lifetime_steps: int,
    lr: float,
) -> tuple[list[float], list[dict[str, torch.Tensor]]]:
    fits: list[float] = []
    phenos: list[dict[str, torch.Tensor]] = []
    for geno in genotypes:
        model = build_student(vocab).to(device)
        model.load_state_dict(copy.deepcopy(geno))
        fit = _lifetime_gd(model, data, steps=lifetime_steps, lr=lr)
        fits.append(fit)
        phenos.append(copy.deepcopy(model.state_dict()))
    return fits, phenos


def _next_gen(
    genotypes: list,
    phenos: list,
    parents: list[int],
    pop_size: int,
    mutate_scale: float,
    inherit_mode: str,
) -> list[dict[str, torch.Tensor]]:
    new_genos: list[dict[str, torch.Tensor]] = []
    for i in range(pop_size):
        p = parents[i % len(parents)]
        src = inherit_weights(genotypes[p], phenos[p], mode=inherit_mode)
        new_genos.append(mutate_state(src, mutate_scale))
    return new_genos


def run_h_bal(**kwargs: Any) -> dict[str, Any]:
    return run_plastic_evo(
        inherit_mode="baldwin", hypothesis="H-BAL", **kwargs
    )
