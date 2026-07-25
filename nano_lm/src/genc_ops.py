"""H-GENC: evolve context/serve genome under BUD; Pareto vs PACK parent."""

from __future__ import annotations

import random
from typing import Any, Mapping, Sequence

from lat_ops import EPS_LP
from tchr_ops import lp_finite

__all__ = [
    "EPS_LP",
    "K_RETRIEVE",
    "CHUNK_LENS",
    "STRIDES",
    "QUANT_BITS",
    "EXIT_DEPTHS",
    "POP_MAX",
    "GencGene",
    "parent_genc_gene",
    "clamp_genc_gene",
    "random_genc_gene",
    "mutate_genc_gene",
    "under_bud_wall",
    "dominates_code_wall",
    "pareto_front_indices",
    "decide_hgenc",
]

GencGene = dict[str, Any]
K_RETRIEVE = (0, 1, 2)
CHUNK_LENS = (32, 64, 128)
STRIDES = (16, 32, 64)
QUANT_BITS = (8, 16)
EXIT_DEPTHS = (1, 2)
POP_MAX = 8


def parent_genc_gene() -> GencGene:
    """PACK/EARLY default: no retrieve, serial-ish chunk, fp16, patient exit."""
    return clamp_genc_gene(
        {
            "k_retrieve": 0,
            "chunk_len": 128,
            "stride": 64,
            "quant_bits": 16,
            "exit_depth": 2,
        }
    )


def clamp_genc_gene(gene: GencGene) -> GencGene:
    """
    GIVEN raw context/serve knobs
    WHEN clamping
    THEN each field snaps to its codebook.
    """
    k = int(round(float(gene["k_retrieve"])))
    c = int(round(float(gene["chunk_len"])))
    s = int(round(float(gene["stride"])))
    q = int(round(float(gene["quant_bits"])))
    e = int(round(float(gene["exit_depth"])))
    return {
        "k_retrieve": min(K_RETRIEVE, key=lambda x: abs(x - k)),
        "chunk_len": min(CHUNK_LENS, key=lambda x: abs(x - c)),
        "stride": min(STRIDES, key=lambda x: abs(x - s)),
        "quant_bits": min(QUANT_BITS, key=lambda x: abs(x - q)),
        "exit_depth": min(EXIT_DEPTHS, key=lambda x: abs(x - e)),
    }


def random_genc_gene(rng: random.Random) -> GencGene:
    return clamp_genc_gene(
        {
            "k_retrieve": rng.choice(K_RETRIEVE),
            "chunk_len": rng.choice(CHUNK_LENS),
            "stride": rng.choice(STRIDES),
            "quant_bits": rng.choice(QUANT_BITS),
            "exit_depth": rng.choice(EXIT_DEPTHS),
        }
    )


def mutate_genc_gene(gene: GencGene, rng: random.Random) -> GencGene:
    g = dict(clamp_genc_gene(gene))
    key = rng.choice(
        ["k_retrieve", "chunk_len", "stride", "quant_bits", "exit_depth"]
    )
    book = {
        "k_retrieve": K_RETRIEVE,
        "chunk_len": CHUNK_LENS,
        "stride": STRIDES,
        "quant_bits": QUANT_BITS,
        "exit_depth": EXIT_DEPTHS,
    }[key]
    i = book.index(int(g[key]))
    i = max(0, min(len(book) - 1, i + rng.choice([-1, 0, 1])))
    g[key] = book[i]
    return clamp_genc_gene(g)


def under_bud_wall(
    util_wall: float, parent_wall: float, *, slack_ms: float = 0.0
) -> bool:
    """BUD wall: util must not exceed parent wall (+ optional slack)."""
    return float(util_wall) <= float(parent_wall) + float(slack_ms)


def dominates_code_wall(
    a: Mapping[str, float], b: Mapping[str, float]
) -> bool:
    """
    GIVEN two (code_lp, wall) points (higher code better, lower wall better)
    WHEN checking domination
    THEN true iff a ≥ b on both axes and strict on at least one.
    """
    a_c, a_w = float(a["mean_code_lp"]), float(a["mean_wall_ms"])
    b_c, b_w = float(b["mean_code_lp"]), float(b["mean_wall_ms"])
    ge = a_c >= b_c and a_w <= b_w
    strict = a_c > b_c or a_w < b_w
    return bool(ge and strict)


def pareto_front_indices(points: Sequence[Mapping[str, float]]) -> list[int]:
    """Indices of non-dominated points on code_lp × wall."""
    out: list[int] = []
    for i, p in enumerate(points):
        dominated = False
        for j, q in enumerate(points):
            if i == j:
                continue
            if dominates_code_wall(q, p):
                dominated = True
                break
        if not dominated:
            out.append(i)
    return out


def decide_hgenc(
    *,
    parent: Mapping[str, float],
    best: Mapping[str, float],
    n_rows: int,
    eps_lp: float = EPS_LP,
    wall_slack_ms: float = 0.0,
) -> str:
    """
    GIVEN PACK/EARLY parent vs best GENC genome on prog@128 (eval)
    WHEN deciding genetic serve under BUD
    THEN PROMOTE iff rows ok, story+code ≥ parent−ε, wall under BUD,
         and (code↑ or wall↓); else KILL.
    """
    if int(n_rows) < 1:
        return "KILL (no scored rows)"
    p_story = float(parent.get("mean_story_lp", float("-inf")))
    b_story = float(best.get("mean_story_lp", float("-inf")))
    p_code = float(parent.get("mean_code_lp", float("-inf")))
    b_code = float(best.get("mean_code_lp", float("-inf")))
    p_wall = float(parent.get("mean_wall_ms", float("nan")))
    b_wall = float(best.get("mean_wall_ms", float("nan")))
    if not all(lp_finite(x) for x in (p_story, b_story, p_code, b_code)):
        return "KILL (teacher_lp not finite)"
    if b_story < p_story - float(eps_lp):
        return (
            f"KILL (story_lp {b_story:.4f} < C0−ε {p_story - eps_lp:.4f})"
        )
    if b_code < p_code - float(eps_lp):
        return f"KILL (code_lp {b_code:.4f} < C0−ε {p_code - eps_lp:.4f})"
    if not under_bud_wall(b_wall, p_wall, slack_ms=wall_slack_ms):
        return f"KILL (wall {b_wall:.0f} over BUD parent {p_wall:.0f})"
    code_win = b_code > p_code
    wall_win = b_wall < p_wall
    if not (code_win or wall_win):
        return "KILL (no code↑ and no wall↓ vs PACK parent)"
    wins = []
    if code_win:
        wins.append("code↑")
    if wall_win:
        wins.append("wall↓")
    return "PROMOTE (GENC under BUD; " + "+".join(wins) + ")"
