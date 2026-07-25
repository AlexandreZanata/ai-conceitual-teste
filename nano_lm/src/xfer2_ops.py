"""H-XFER2: PACK-only transfer deepen on OOD/elongated packs (optional BPACK)."""

from __future__ import annotations

from typing import Mapping

from bpack_ops import decide_hbpack
from chunk_ops import LONG_TARGET_TOKENS
from xfer_ops import XFER_ELONGATE_TOKENS, verdict_pack

__all__ = [
    "XFER2_ELONGATE_TOKENS",
    "XFER2_PACKS",
    "XFER2_RECIPES",
    "LONG_TARGET_TOKENS",
    "decide_hxfer2",
    "verdict_pack",
    "verdict_bpack",
]

# Same elongate depth as H-XFER; ood_long uses this on OOD texts.
XFER2_ELONGATE_TOKENS = XFER_ELONGATE_TOKENS
XFER2_PACKS = ("elongated", "ood", "ood_long")
XFER2_RECIPES = ("H-PACK",)


def verdict_bpack(stats: Mapping[str, Mapping[str, float]]) -> str:
    """Apply frozen H-BPACK dual gate on one transfer pack (optional report)."""
    return decide_hbpack(stats)


def decide_hxfer2(verdicts: Mapping[str, Mapping[str, str]]) -> str:
    """
    GIVEN per-pack H-PACK dual-gate strings (optional BPACK ignored for gate)
    WHEN aggregating PACK-only transfer deepen
    THEN PROMOTE iff every XFER2 pack starts with PROMOTE; else KILL first fail.
    """
    pack_map = verdicts.get("H-PACK")
    if pack_map is None:
        return "needs H-PACK verdicts"
    for pack in XFER2_PACKS:
        v = pack_map.get(pack)
        if v is None:
            return f"needs H-PACK/{pack}"
        if not str(v).startswith("PROMOTE"):
            return f"KILL (transfer fail H-PACK/{pack}: {v})"
    return "PROMOTE (PACK holds on elongated/ood/ood_long)"
