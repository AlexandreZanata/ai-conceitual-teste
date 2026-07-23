"""H-DRAFT: evolve speculative draft knobs; dual gate vs B4."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP

__all__ = [
    "DRAFT_LENS",
    "DraftGene",
    "clamp_draft_gene",
    "random_draft_gene",
    "mutate_draft_gene",
    "decide_hdraft",
]

DraftGene = dict[str, Any]
DRAFT_LENS = (1, 2, 4, 8)


def clamp_draft_gene(gene: DraftGene) -> DraftGene:
    """
    GIVEN raw draft knobs
    WHEN clamping
    THEN draft_len ∈ DRAFT_LENS and temp/top_p in safe ranges.
    """
    d = int(round(float(gene["draft_len"])))
    draft_len = min(DRAFT_LENS, key=lambda x: abs(x - d))
    temp = float(min(1.5, max(0.2, float(gene["temperature"]))))
    top_p = float(min(1.0, max(0.5, float(gene["top_p"]))))
    return {"draft_len": int(draft_len), "temperature": temp, "top_p": top_p}


def random_draft_gene(rng: random.Random) -> DraftGene:
    return clamp_draft_gene(
        {
            "draft_len": rng.choice(DRAFT_LENS),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )


def mutate_draft_gene(gene: DraftGene, rng: random.Random) -> DraftGene:
    g = dict(clamp_draft_gene(gene))
    if rng.random() < 0.5:
        i = DRAFT_LENS.index(int(g["draft_len"]))
        i = max(0, min(len(DRAFT_LENS) - 1, i + rng.choice([-1, 0, 1])))
        g["draft_len"] = DRAFT_LENS[i]
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    return clamp_draft_gene(g)


def decide_hdraft(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DRAFT vs B4
    WHEN deciding
    THEN PROMOTE only if quality ≥ B4−ε and wall < B4; else KILL.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s["mean_lp"]) < float(b4["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs B4)"
    if not (float(s["mean_wall"]) < float(b4["mean_wall"])):
        return "KILL (no speedup vs B4)"
    return "PROMOTE (quality@wall vs B4)"
