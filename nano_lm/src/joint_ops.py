"""H-JOINT: joint curriculum ∪ early-exit gene; free-lunch vs CURL+EARLY."""

from __future__ import annotations

import random
from typing import Any, Mapping

from early_ops import clamp_early_gene, mutate_early_gene, random_early_gene

__all__ = [
    "JOINT_LOS",
    "JOINT_STAGES",
    "JointGene",
    "clamp_joint_gene",
    "random_joint_gene",
    "mutate_joint_gene",
    "decide_hjoint",
]

JOINT_LOS = (8, 16)
JOINT_STAGES = (3, 5)
JointGene = dict[str, Any]


def clamp_joint_gene(gene: JointGene) -> JointGene:
    """
    GIVEN raw joint gene
    WHEN clamping
    THEN seq_lo/n_stages on codebooks; early fields via clamp_early_gene.
    """
    lo = int(round(float(gene["seq_lo"])))
    seq_lo = min(JOINT_LOS, key=lambda x: abs(x - lo))
    st = int(round(float(gene["n_stages"])))
    n_stages = min(JOINT_STAGES, key=lambda x: abs(x - st))
    early = clamp_early_gene(gene)
    out = dict(early)
    out["seq_lo"] = int(seq_lo)
    out["n_stages"] = int(n_stages)
    return out


def random_joint_gene(rng: random.Random) -> JointGene:
    g = random_early_gene(rng)
    g["seq_lo"] = rng.choice(list(JOINT_LOS))
    g["n_stages"] = rng.choice(list(JOINT_STAGES))
    return clamp_joint_gene(g)


def mutate_joint_gene(gene: JointGene, rng: random.Random) -> JointGene:
    g = dict(clamp_joint_gene(gene))
    if rng.random() < 0.4:
        i = list(JOINT_LOS).index(int(g["seq_lo"]))
        i = max(0, min(len(JOINT_LOS) - 1, i + rng.choice([-1, 0, 1])))
        g["seq_lo"] = int(JOINT_LOS[i])
    if rng.random() < 0.4:
        j = list(JOINT_STAGES).index(int(g["n_stages"]))
        j = max(0, min(len(JOINT_STAGES) - 1, j + rng.choice([-1, 0, 1])))
        g["n_stages"] = int(JOINT_STAGES[j])
    early = mutate_early_gene(g, rng)
    early["seq_lo"] = int(g["seq_lo"])
    early["n_stages"] = int(g["n_stages"])
    return clamp_joint_gene(early)


def decide_hjoint(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-JOINT vs H-CURL default and H-EARLY@B2
    WHEN deciding
    THEN PROMOTE iff lp > CURL and lp > EARLY@B2; else KILL.
    """
    curl = stats.get("H-CURL")
    early = stats.get("H-EARLY")
    if curl is None or early is None:
        return "needs H-CURL+H-EARLY controls"
    if float(s["mean_lp"]) <= float(curl["mean_lp"]) + 1e-6:
        return "KILL (≤ CURL default decode)"
    if float(s["mean_lp"]) <= float(early["mean_lp"]) + 1e-6:
        return "KILL (≤ H-EARLY@B2)"
    return "PROMOTE (beats CURL + H-EARLY@B2)"
