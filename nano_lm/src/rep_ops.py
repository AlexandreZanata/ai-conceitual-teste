"""H-REP: repetition-penalty / no-repeat n-gram under frozen EARLY tip."""

from __future__ import annotations

import random
from typing import Any, Mapping

import torch

__all__ = [
    "REP_PENALTIES",
    "NGRAM_SIZES",
    "RepGene",
    "clamp_rep_gene",
    "random_rep_gene",
    "mutate_rep_gene",
    "apply_repetition_penalty",
    "ban_ngram_logits",
    "decide_hrep",
]

RepGene = dict[str, Any]
REP_PENALTIES = (1.0, 1.05, 1.1, 1.2, 1.35)
NGRAM_SIZES = (0, 2, 3)


def clamp_rep_gene(gene: Mapping[str, Any], tip: Mapping[str, Any]) -> RepGene:
    out = dict(tip)
    pen = float(gene["rep_penalty"])
    out["rep_penalty"] = float(min(REP_PENALTIES, key=lambda x: abs(x - pen)))
    ng = int(round(float(gene["no_repeat_ngram"])))
    out["no_repeat_ngram"] = int(min(NGRAM_SIZES, key=lambda x: abs(x - ng)))
    return out


def random_rep_gene(rng: random.Random, tip: Mapping[str, Any]) -> RepGene:
    return clamp_rep_gene(
        {
            "rep_penalty": rng.choice(REP_PENALTIES),
            "no_repeat_ngram": rng.choice(NGRAM_SIZES),
        },
        tip,
    )


def mutate_rep_gene(
    gene: RepGene, rng: random.Random, tip: Mapping[str, Any]
) -> RepGene:
    g = dict(gene)
    if rng.random() < 0.5:
        g["rep_penalty"] = rng.choice(REP_PENALTIES)
    else:
        g["no_repeat_ngram"] = rng.choice(NGRAM_SIZES)
    return clamp_rep_gene(g, tip)


def apply_repetition_penalty(
    logits: torch.Tensor, ids: torch.Tensor, *, penalty: float
) -> torch.Tensor:
    """
    GIVEN next-token logits [B,V] and full id sequences [B,T]
    WHEN applying HF-style repetition penalty
    THEN down-weight tokens already present (no-op if penalty≈1).
    """
    if abs(float(penalty) - 1.0) < 1e-9:
        return logits
    out = logits.clone()
    pen = float(penalty)
    for b in range(int(ids.shape[0])):
        for tid in set(int(x) for x in ids[b].tolist()):
            score = out[b, tid]
            out[b, tid] = score * pen if float(score) < 0.0 else score / pen
    return out


def ban_ngram_logits(
    logits: torch.Tensor, ids: torch.Tensor, *, ngram: int
) -> torch.Tensor:
    """
    GIVEN logits and sequences
    WHEN no_repeat_ngram ≥ 2
    THEN set −inf on tokens that would recreate a seen n-gram.
    """
    n = int(ngram)
    if n < 2:
        return logits
    out = logits.clone()
    for b in range(int(ids.shape[0])):
        gen = [int(x) for x in ids[b].tolist()]
        if len(gen) < n:
            continue
        banned: dict[tuple[int, ...], set[int]] = {}
        for i in range(len(gen) - n + 1):
            pref = tuple(gen[i : i + n - 1])
            banned.setdefault(pref, set()).add(gen[i + n - 1])
        pref = tuple(gen[-(n - 1) :])
        for tok in banned.get(pref, ()):
            out[b, tok] = float("-inf")
    return out


def decide_hrep(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
) -> str:
    """
    GIVEN H-REP vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp > EARLY and wall ≤ EARLY; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) <= float(tip["mean_lp"]):
        return "KILL (no quality win vs H-EARLY)"
    if float(s["mean_wall"]) > float(tip["mean_wall"]):
        return "KILL (worse wall vs H-EARLY)"
    return "PROMOTE (quality@wall vs H-EARLY)"
