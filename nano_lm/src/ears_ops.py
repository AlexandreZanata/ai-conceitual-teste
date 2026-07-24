"""H-EARS: schedule early-exit thr by prompt length + remaining budget."""

from __future__ import annotations

import random
from typing import Any, Mapping

from early_ops import PATIENCES, clamp_early_gene
from lat_ops import EPS_LP

__all__ = [
    "PROMPT_REFS",
    "EarsGene",
    "scheduled_conf",
    "clamp_ears_gene",
    "random_ears_gene",
    "mutate_ears_gene",
    "decide_hears",
]

EarsGene = dict[str, Any]
PROMPT_REFS = (16, 32, 64)


def scheduled_conf(
    *,
    base_thr: float,
    prompt_len: int,
    n_new: int,
    max_new: int,
    len_coef: float,
    budget_coef: float,
    prompt_ref: int,
) -> float:
    """
    GIVEN base thr + prompt/budget schedule knobs
    WHEN computing effective conf_threshold
    THEN clamp to [0.5, 0.99].
    """
    ref = max(1, int(prompt_ref))
    len_term = float(len_coef) * (float(prompt_len) / float(ref) - 1.0)
    rem = max(0, int(max_new) - int(n_new))
    frac = 1.0 - float(rem) / float(max(1, int(max_new)))
    budget_term = float(budget_coef) * frac
    return float(min(0.99, max(0.5, float(base_thr) + len_term + budget_term)))


def clamp_ears_gene(gene: EarsGene) -> EarsGene:
    """
    GIVEN raw ears knobs
    WHEN clamping
    THEN early fields + len/budget coefs + prompt_ref codebook.
    """
    base = clamp_early_gene(gene)
    base["len_coef"] = float(min(0.25, max(-0.25, float(gene.get("len_coef", 0.0)))))
    base["budget_coef"] = float(
        min(0.15, max(-0.35, float(gene.get("budget_coef", -0.1))))
    )
    pref = int(round(float(gene.get("prompt_ref", 32))))
    base["prompt_ref"] = int(min(PROMPT_REFS, key=lambda x: abs(x - pref)))
    return base


def random_ears_gene(rng: random.Random) -> EarsGene:
    g = clamp_early_gene(
        {
            "min_new": rng.choice((4, 8, 12)),
            "patience": rng.choice(PATIENCES),
            "conf_threshold": rng.uniform(0.55, 0.95),
            "n": rng.choice([1, 2]),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )
    g["len_coef"] = rng.uniform(-0.2, 0.2)
    g["budget_coef"] = rng.uniform(-0.3, 0.1)
    g["prompt_ref"] = rng.choice(list(PROMPT_REFS))
    return clamp_ears_gene(g)


def mutate_ears_gene(gene: EarsGene, rng: random.Random) -> EarsGene:
    g = dict(clamp_ears_gene(gene))
    g["conf_threshold"] = float(g["conf_threshold"]) + 0.05 * rng.uniform(-1, 1)
    g["n"] = int(g["n"]) + rng.choice([-1, 0, 1])
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    g["len_coef"] = float(g["len_coef"]) + 0.05 * rng.uniform(-1, 1)
    g["budget_coef"] = float(g["budget_coef"]) + 0.05 * rng.uniform(-1, 1)
    if rng.random() < 0.3:
        g["prompt_ref"] = rng.choice(list(PROMPT_REFS))
    if rng.random() < 0.4:
        from early_ops import MIN_NEWS

        i = MIN_NEWS.index(int(g["min_new"]))
        i = max(0, min(len(MIN_NEWS) - 1, i + rng.choice([-1, 0, 1])))
        g["min_new"] = MIN_NEWS[i]
    if rng.random() < 0.4:
        k = PATIENCES.index(int(g["patience"]))
        k = max(0, min(len(PATIENCES) - 1, k + rng.choice([-1, 0, 1])))
        g["patience"] = PATIENCES[k]
    return clamp_ears_gene(g)


def decide_hears(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-EARS vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and wall < EARLY; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-EARLY)"
    return "PROMOTE (scheduled thr vs H-EARLY)"
