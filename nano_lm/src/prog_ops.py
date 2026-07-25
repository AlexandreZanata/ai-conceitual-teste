"""H-PROG: programming domain capacity — PACK tip gate on curated code/docs."""

from __future__ import annotations

from typing import Mapping

from chunk_ops import LONG_TARGET_TOKENS
from xfer_ops import verdict_pack

__all__ = [
    "PROG_PACK",
    "LONG_TARGET_TOKENS",
    "decide_hprog",
    "verdict_pack",
]

PROG_PACK = "prog"


def decide_hprog(verdicts: Mapping[str, str]) -> str:
    """
    GIVEN H-PACK dual-gate string on the programming domain
    WHEN deciding domain capacity
    THEN PROMOTE iff PACK starts with PROMOTE; else KILL.
    """
    v = verdicts.get("H-PACK")
    if v is None:
        return "needs H-PACK verdict"
    if not str(v).startswith("PROMOTE"):
        return f"KILL (PACK tip gate fails on {PROG_PACK}: {v})"
    return f"PROMOTE (PACK tip gate holds on {PROG_PACK} domain)"
