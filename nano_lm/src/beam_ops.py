"""H-BEAM: evolve beam-search knobs; dual gate vs B4."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP

__all__ = [
    "BEAM_WIDTHS",
    "BeamGene",
    "clamp_beam_gene",
    "random_beam_gene",
    "mutate_beam_gene",
    "decide_hbeam",
]

BeamGene = dict[str, Any]
BEAM_WIDTHS = (2, 3, 4, 5)


def clamp_beam_gene(gene: BeamGene) -> BeamGene:
    """
    GIVEN raw beam knobs
    WHEN clamping
    THEN beam_width ∈ BEAM_WIDTHS and length_penalty in [0, 2].
    """
    w = int(round(float(gene["beam_width"])))
    beam_width = min(BEAM_WIDTHS, key=lambda x: abs(x - w))
    lp = float(min(2.0, max(0.0, float(gene["length_penalty"]))))
    return {"beam_width": int(beam_width), "length_penalty": lp}


def random_beam_gene(rng: random.Random) -> BeamGene:
    return clamp_beam_gene(
        {
            "beam_width": rng.choice(BEAM_WIDTHS),
            "length_penalty": rng.uniform(0.0, 1.5),
        }
    )


def mutate_beam_gene(gene: BeamGene, rng: random.Random) -> BeamGene:
    g = dict(clamp_beam_gene(gene))
    if rng.random() < 0.5:
        i = BEAM_WIDTHS.index(int(g["beam_width"]))
        i = max(0, min(len(BEAM_WIDTHS) - 1, i + rng.choice([-1, 0, 1])))
        g["beam_width"] = BEAM_WIDTHS[i]
    g["length_penalty"] = float(g["length_penalty"]) + 0.2 * rng.uniform(-1, 1)
    return clamp_beam_gene(g)


def decide_hbeam(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-BEAM vs B4
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
