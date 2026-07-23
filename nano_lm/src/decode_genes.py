"""Decode-policy genes for H-DEC (temp, top_p, N, K, B, H, use_mae)."""

from __future__ import annotations

import random
from typing import Any


Gene = dict[str, Any]

BOUNDS = {
    "temperature": (0.2, 1.5),
    "top_p": (0.5, 1.0),
    "n": (1, 6),
    "k": (1, 4),
    "block": (1, 2),
    "horizon": (1, 4),
}


def clamp_gene(gene: Gene) -> Gene:
    """
    GIVEN raw decode knobs WHEN clamping THEN all fields stay in BOUNDS
    and use_mae is bool.
    """
    out: Gene = {}
    for key, (lo, hi) in BOUNDS.items():
        v = gene[key]
        if key in {"n", "k", "block", "horizon"}:
            out[key] = int(min(hi, max(lo, round(float(v)))))
        else:
            out[key] = float(min(hi, max(lo, float(v))))
    out["use_mae"] = bool(gene.get("use_mae", False))
    return out


def default_bon_gene() -> Gene:
    """Fixed BoN control knobs (matches B4 smoke)."""
    return clamp_gene(
        {
            "temperature": 0.8,
            "top_p": 0.9,
            "n": 4,
            "k": 4,
            "block": 2,
            "horizon": 2,
            "use_mae": False,
        }
    )


def random_gene(rng: random.Random) -> Gene:
    return clamp_gene(
        {
            "temperature": rng.uniform(*BOUNDS["temperature"]),
            "top_p": rng.uniform(*BOUNDS["top_p"]),
            "n": rng.randint(*BOUNDS["n"]),
            "k": rng.randint(*BOUNDS["k"]),
            "block": rng.randint(*BOUNDS["block"]),
            "horizon": rng.randint(*BOUNDS["horizon"]),
            "use_mae": rng.random() < 0.15,
        }
    )


def mutate_gene(gene: Gene, rng: random.Random, *, scale: float = 0.15) -> Gene:
    """
    GIVEN a clamped gene WHEN mutating THEN return a new clamped gene
    (ints nudge by ±1 with noise; use_mae may flip).
    """
    g = dict(gene)
    g["temperature"] = float(g["temperature"]) + scale * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + scale * rng.uniform(-1, 1)
    for key in ("n", "k", "block", "horizon"):
        g[key] = int(g[key]) + rng.choice([-1, 0, 1])
    if rng.random() < 0.2:
        g["use_mae"] = not bool(g["use_mae"])
    return clamp_gene(g)
