"""H-ELI: strong elitism — keep elite-k unchanged; mutate only the rest."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import torch

from data_tiny import iter_token_batches, load_tokenizer
from elite_ops import diversity_collapsed, fill_plan, select_elite_indices
from hyp_sel import mutate_state
from student_model import build_student, count_params
from train_ce import ce_loss


def _fitness(model: Any, probe: torch.Tensor) -> float:
    with torch.no_grad():
        return -float(ce_loss(model(probe).logits, probe).item())


def _pop_diversity(states: list[dict[str, torch.Tensor]]) -> float:
    """Mean pairwise L2 over flattened float tensors (CPU)."""
    if len(states) < 2:
        return 0.0
    vecs = []
    for st in states:
        parts = [
            v.detach().float().reshape(-1).cpu()
            for v in st.values()
            if v.dtype.is_floating_point
        ]
        vecs.append(torch.cat(parts))
    total = 0.0
    n = 0
    for i in range(len(vecs)):
        for j in range(i + 1, len(vecs)):
            total += float(torch.norm(vecs[i] - vecs[j]).item())
            n += 1
    return total / max(n, 1)


def _next_pop(
    vocab: int,
    device: torch.device,
    states: list[dict[str, torch.Tensor]],
    elites: list[int],
    plan: list[str],
    mutate_scale: float,
) -> list[Any]:
    out = []
    e_i = 0
    m_i = 0
    for slot in plan:
        child = build_student(vocab).to(device)
        if slot == "elite":
            child.load_state_dict(copy.deepcopy(states[elites[e_i]]))
            e_i += 1
        else:
            parent = elites[m_i % len(elites)]
            child.load_state_dict(mutate_state(states[parent], mutate_scale))
            m_i += 1
        child.eval()
        out.append(child)
    return out


def run_h_eli(
    *,
    tokenizer_id: str,
    cache_dir: Path,
    device: torch.device,
    pop_size: int,
    generations: int,
    elite_k: int,
    mutate_scale: float,
    seq_len: int,
    batch_size: int,
    max_examples: int,
    seed: int,
    out_path: Path,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    tok = load_tokenizer(tokenizer_id, cache_dir)
    vocab = len(tok)
    pop = [build_student(vocab).to(device) for _ in range(pop_size)]
    for m in pop:
        m.eval()
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
        raise RuntimeError("H-ELI: no training batches")
    probe = data[0]
    best_state = None
    best_fit = float("-inf")
    history: list[float] = []
    div_hist: list[float] = []
    plan = fill_plan(pop_size, elite_k)
    for _gen in range(generations):
        fits = [_fitness(m, probe) for m in pop]
        states = [copy.deepcopy(m.state_dict()) for m in pop]
        div_hist.append(_pop_diversity(states))
        elites = select_elite_indices(fits, elite_k)
        history.append(fits[elites[0]])
        if fits[elites[0]] > best_fit:
            best_fit = fits[elites[0]]
            best_state = states[elites[0]]
        pop = _next_pop(vocab, device, states, elites, plan, mutate_scale)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    collapsed = diversity_collapsed(div_hist[0], div_hist[-1]) if div_hist else True
    out_path.parent.mkdir(parents=True, exist_ok=True)
    assert best_state is not None
    torch.save({"model": best_state, "seed": seed}, out_path)
    return {
        "hypothesis": "H-ELI",
        "params": count_params(build_student(vocab)),
        "best_fit": best_fit,
        "history": history,
        "diversity": div_hist,
        "diversity_collapsed": collapsed,
        "elite_k": elite_k,
        "out_path": str(out_path),
    }
