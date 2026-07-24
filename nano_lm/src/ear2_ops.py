"""H-EAR2: widened early-exit gene; dual wall vs H-EARLY tip."""

from __future__ import annotations

import math
import random
from typing import Any, Mapping

import torch

from early_ops import PATIENCES, clamp_early_gene
from lat_ops import EPS_LP

__all__ = [
    "MIN_NEWS2",
    "MAX_NEWS",
    "CONF_METRICS",
    "Ear2Gene",
    "clamp_ear2_gene",
    "random_ear2_gene",
    "mutate_ear2_gene",
    "conf_score",
    "decide_hear2",
]

Ear2Gene = dict[str, Any]
MIN_NEWS2 = (2, 4, 6, 8, 12, 16)
MAX_NEWS = (8, 12, 16, 24, 32)
CONF_METRICS = ("max_p", "margin", "entropy")


def conf_score(probs: torch.Tensor, metric: str) -> torch.Tensor:
    """
    GIVEN token probs [B, V] and metric name
    WHEN scoring confidence
    THEN higher = more confident (same thr scale as max_p).
    """
    if metric == "margin":
        top2 = torch.topk(probs, k=2, dim=-1).values
        return top2[:, 0] - top2[:, 1]
    if metric == "entropy":
        ent = -(probs * (probs + 1e-12).log()).sum(dim=-1)
        return 1.0 - ent / math.log(float(probs.shape[-1]))
    return probs.max(dim=-1).values


def clamp_ear2_gene(gene: Ear2Gene) -> Ear2Gene:
    """
    GIVEN raw ear2 knobs
    WHEN clamping
    THEN early fields + max_new on codebook + conf_metric ∈ CONF_METRICS.
    """
    base = clamp_early_gene(gene)
    mn = int(round(float(gene.get("min_new", base["min_new"]))))
    base["min_new"] = int(min(MIN_NEWS2, key=lambda x: abs(x - mn)))
    mx = int(round(float(gene.get("max_new", 16))))
    base["max_new"] = int(min(MAX_NEWS, key=lambda x: abs(x - mx)))
    if int(base["max_new"]) < int(base["min_new"]):
        ups = [x for x in MAX_NEWS if x >= int(base["min_new"])]
        base["max_new"] = int(ups[0] if ups else MAX_NEWS[-1])
    metric = str(gene.get("conf_metric", "max_p"))
    base["conf_metric"] = metric if metric in CONF_METRICS else "max_p"
    return base


def random_ear2_gene(rng: random.Random) -> Ear2Gene:
    g = clamp_early_gene(
        {
            "min_new": rng.choice(MIN_NEWS2),
            "patience": rng.choice(PATIENCES),
            "conf_threshold": rng.uniform(0.55, 0.95),
            "n": rng.choice([1, 2]),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )
    g["max_new"] = rng.choice(MAX_NEWS)
    g["conf_metric"] = rng.choice(list(CONF_METRICS))
    return clamp_ear2_gene(g)


def mutate_ear2_gene(gene: Ear2Gene, rng: random.Random) -> Ear2Gene:
    g = dict(clamp_ear2_gene(gene))
    if rng.random() < 0.4:
        i = MIN_NEWS2.index(int(g["min_new"]))
        i = max(0, min(len(MIN_NEWS2) - 1, i + rng.choice([-1, 0, 1])))
        g["min_new"] = MIN_NEWS2[i]
    if rng.random() < 0.4:
        j = MAX_NEWS.index(int(g["max_new"]))
        j = max(0, min(len(MAX_NEWS) - 1, j + rng.choice([-1, 0, 1])))
        g["max_new"] = MAX_NEWS[j]
    if rng.random() < 0.3:
        g["conf_metric"] = rng.choice(list(CONF_METRICS))
    g["conf_threshold"] = float(g["conf_threshold"]) + 0.05 * rng.uniform(-1, 1)
    g["n"] = int(g["n"]) + rng.choice([-1, 0, 1])
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    if rng.random() < 0.4:
        k = PATIENCES.index(int(g["patience"]))
        k = max(0, min(len(PATIENCES) - 1, k + rng.choice([-1, 0, 1])))
        g["patience"] = PATIENCES[k]
    return clamp_ear2_gene(g)


def decide_hear2(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-EAR2 vs H-EARLY tip
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
    return "PROMOTE (wider early gene vs H-EARLY)"
