"""H-THIN: thinner CURL student; claim with frozen EARLY genes."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from student_model import THIN_MAX_PARAMS

__all__ = ["THIN_MAX_PARAMS", "decide_hthin"]


def decide_hthin(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-THIN vs H-CURL on same EARLY decode
    WHEN deciding
    THEN PROMOTE iff lp ≥ CURL−ε and wall < CURL; else KILL.
    """
    tip = stats.get("H-CURL")
    if tip is None:
        return "needs H-CURL control (same EARLY decode)"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-CURL)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-CURL)"
    return "PROMOTE (thin CURL + EARLY vs tip)"
