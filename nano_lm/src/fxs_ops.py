"""Champion stack helpers for H-FXS: crossover → mutate → layer shock."""

from __future__ import annotations

import random
from typing import Mapping

import torch

from hyp_sel import mutate_state
from sho_ops import pick_prefix, shock_state
from xov_ops import blend_state_dicts

PARENTS = ("H-FIT", "H-XOV", "H-SHO")


def breed_fxs_state(
    parent_a: Mapping[str, torch.Tensor],
    parent_b: Mapping[str, torch.Tensor],
    fresh: Mapping[str, torch.Tensor],
    prefixes: list[str],
    rng: random.Random,
    mutate_scale: float,
) -> tuple[dict[str, torch.Tensor], str]:
    """
    GIVEN two parents, a fresh init, and layer prefixes
    WHEN breeding an H-FXS child
    THEN crossover → mutate → shock one random layer; return state + prefix.
    """
    if mutate_scale < 0.0:
        raise ValueError("breed_fxs_state: mutate_scale must be >= 0")
    blended = blend_state_dicts(dict(parent_a), dict(parent_b), rng)
    mutated = mutate_state(blended, mutate_scale)
    prefix = pick_prefix(prefixes, rng.randrange(len(prefixes)))
    return shock_state(mutated, fresh, prefix), prefix


def decide_hfxs(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-FXS stats and H-FIT/H-XOV controls
    WHEN deciding promote/kill
    THEN PROMOTE iff strictly better than max(H-FIT, H-XOV) mean_lp.
    """
    fit = stats.get("H-FIT")
    xov = stats.get("H-XOV")
    if fit is None or xov is None:
        return "needs H-FIT+H-XOV control"
    best = max(float(fit["mean_lp"]), float(xov["mean_lp"]))
    if float(s["mean_lp"]) > best + 1e-6:
        return "PROMOTE (beats max FIT/XOV)"
    return "KILL / hold (≤ max FIT/XOV)"
