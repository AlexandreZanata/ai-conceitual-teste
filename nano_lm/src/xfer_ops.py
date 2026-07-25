"""H-XFER: transfer audit — PACK/QPACK/TPACK dual gates on new prompt packs."""

from __future__ import annotations

from typing import Mapping

from chunk_ops import LONG_TARGET_TOKENS
from pack_ops import decide_hpack
from qpack_ops import decide_hqpack
from tpack_ops import decide_htpack

__all__ = [
    "XFER_ELONGATE_TOKENS",
    "XFER_PACKS",
    "XFER_RECIPES",
    "LONG_TARGET_TOKENS",
    "decide_hxfer",
    "verdict_pack",
    "verdict_qpack",
    "verdict_tpack",
]

# Extra-long prefill vs harness LONG_TARGET_TOKENS=128 (stops elongate overfit).
XFER_ELONGATE_TOKENS = 256
XFER_PACKS = ("heldout", "elongated", "ood")
XFER_RECIPES = ("H-PACK", "H-QPACK", "H-TPACK")


def verdict_pack(stats: Mapping[str, Mapping[str, float]]) -> str:
    """Apply frozen H-PACK dual gate on one transfer pack."""
    return decide_hpack(stats)


def verdict_qpack(stats: Mapping[str, Mapping[str, float]]) -> str:
    """Apply frozen H-QPACK dual gate on one transfer pack."""
    s = stats.get("H-FLAYB")
    if s is None:
        return "needs H-FLAYB rows"
    return decide_hqpack(s, stats)


def verdict_tpack(stats: Mapping[str, Mapping[str, float]]) -> str:
    """Apply frozen H-TPACK dual gate on one transfer pack."""
    s = stats.get("H-TPACK")
    if s is None:
        return "needs H-TPACK rows"
    return decide_htpack(s, stats)


def decide_hxfer(verdicts: Mapping[str, Mapping[str, str]]) -> str:
    """
    GIVEN per-recipe per-pack dual-gate strings
    WHEN aggregating transfer audit
    THEN PROMOTE iff every pack×recipe starts with PROMOTE; else KILL first fail.
    """
    for recipe in XFER_RECIPES:
        pack_map = verdicts.get(recipe)
        if pack_map is None:
            return f"needs {recipe} verdicts"
        for pack in XFER_PACKS:
            v = pack_map.get(pack)
            if v is None:
                return f"needs {recipe}/{pack}"
            if not str(v).startswith("PROMOTE"):
                return f"KILL (transfer fail {recipe}/{pack}: {v})"
    return "PROMOTE (PACK/QPACK/TPACK hold on heldout/elongated/ood)"
