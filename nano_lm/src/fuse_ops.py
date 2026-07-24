"""H-FUSE: protocol stack FLASH ⊕ KVSEL (not a tip H-ID)."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hfuse", "EPS_LP"]


def decide_hfuse(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN FLASH⊕KVSEL fuse vs EARLY / FLASH / KVSEL controls
    WHEN deciding
    THEN PROTOCOL iff lp ≥ EARLY−ε and wall < min(FLASH, KVSEL); else KILL.
    Never tip PROMOTE (compose branch closed).
    """
    early = stats.get("H-EARLY")
    flash = stats.get("H-FLASH")
    kvsel = stats.get("H-KVSEL")
    if early is None:
        return "needs H-EARLY control"
    if flash is None:
        return "needs H-FLASH control"
    if kvsel is None:
        return "needs H-KVSEL control"
    if float(s["mean_lp"]) < float(early["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY; do not stack)"
    floor = min(float(flash["mean_wall"]), float(kvsel["mean_wall"]))
    if not (float(s["mean_wall"]) < floor):
        return "KILL (wall ≥ min(FLASH,KVSEL); stack adds no value)"
    return "PROTOCOL (FLASH ⊕ KVSEL; not a tip H-ID)"
