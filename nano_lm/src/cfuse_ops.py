"""H-CFUSE: protocol stack CHUNK ⊕ FUSE (FLASH⊕KVSEL); not a tip H-ID."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hcfuse", "EPS_LP"]


def decide_hcfuse(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN CHUNK⊕FUSE cfuse vs EARLY / CHUNK / FUSE controls
    WHEN deciding
    THEN PROTOCOL iff lp ≥ EARLY−ε and wall < min(CHUNK, FUSE); else KILL.
    Never tip PROMOTE (compose branch closed).
    """
    early = stats.get("H-EARLY")
    chunk = stats.get("H-CHUNK")
    fuse = stats.get("H-FUSE")
    if early is None:
        return "needs H-EARLY control"
    if chunk is None:
        return "needs H-CHUNK control"
    if fuse is None:
        return "needs H-FUSE control"
    if float(s["mean_lp"]) < float(early["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY; do not stack)"
    floor = min(float(chunk["mean_wall"]), float(fuse["mean_wall"]))
    if not (float(s["mean_wall"]) < floor):
        return "KILL (wall ≥ min(CHUNK,FUSE); stack adds no value)"
    return "PROTOCOL (CHUNK ⊕ FUSE; not a tip H-ID)"
