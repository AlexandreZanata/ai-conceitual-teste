"""H-DOM: new short domain capacity — PACK tip gate on howto prompts."""

from __future__ import annotations

from typing import Mapping

from chunk_ops import LONG_TARGET_TOKENS
from xfer_ops import verdict_pack

__all__ = [
    "DOM_PACK",
    "LONG_TARGET_TOKENS",
    "decide_hdom",
    "verdict_pack",
]

DOM_PACK = "howto"


def decide_hdom(verdicts: Mapping[str, str]) -> str:
    """
    GIVEN H-PACK dual-gate string on the new howto domain
    WHEN deciding domain capacity
    THEN PROMOTE iff PACK starts with PROMOTE; else KILL.
    """
    v = verdicts.get("H-PACK")
    if v is None:
        return "needs H-PACK verdict"
    if not str(v).startswith("PROMOTE"):
        return f"KILL (PACK tip gate fails on {DOM_PACK}: {v})"
    return f"PROMOTE (PACK tip gate holds on {DOM_PACK} domain)"
