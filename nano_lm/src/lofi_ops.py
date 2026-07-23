"""Low-fidelity rank helpers for H-LOFI: CE top-k then teacher rescore."""

from __future__ import annotations

from typing import Mapping, Sequence

EPS_LP = 0.05


def top_k_indices(scores: Sequence[float], k: int) -> list[int]:
    """
    GIVEN fitness scores (higher better) and k ≥ 1
    WHEN selecting top-k
    THEN return indices of the k highest scores (ties prefer lower index).
    """
    if k < 1:
        raise ValueError("top_k_indices: k must be >= 1")
    if not scores:
        raise ValueError("top_k_indices: empty scores")
    kk = min(k, len(scores))
    ranked = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    return ranked[:kk]


def teacher_forward_budget(
    *, pop_size: int, generations: int, n_prompts: int, top_k: int
) -> tuple[int, int]:
    """
    GIVEN pop/gens/prompts and rescore width
    WHEN counting teacher completion scores
    THEN return (lofi_forwards, full_hfit_forwards).
    """
    if min(pop_size, generations, n_prompts, top_k) < 1:
        raise ValueError("teacher_forward_budget: all args must be >= 1")
    k = min(top_k, pop_size)
    lofi = generations * k * n_prompts
    full = generations * pop_size * n_prompts
    return lofi, full


def wall_saved(lofi_forwards: int, full_forwards: int) -> bool:
    """True when H-LOFI uses strictly fewer teacher forwards than full H-FIT."""
    return int(lofi_forwards) < int(full_forwards)


def decide_hlofi(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-LOFI stats vs H-FIT
    WHEN deciding
    THEN KILL if quality < H-FIT−ε or no wall_save; else PROMOTE.
    """
    hfit = stats.get("H-FIT")
    if hfit is None:
        return "needs H-FIT control"
    if float(s["mean_lp"]) < float(hfit["mean_lp"]) - EPS_LP:
        return "KILL (worse quality than H-FIT)"
    if float(s.get("wall_save", 0.0)) <= 0.0:
        return "KILL (no wall save)"
    return "PROMOTE (quality@wall vs H-FIT)"
