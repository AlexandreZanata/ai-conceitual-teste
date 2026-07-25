"""Score H-DOM PACK rows into tip-gate verdict."""

from __future__ import annotations

from typing import Any

from xfer_score import means_decode
from dom_ops import verdict_pack

__all__ = ["means_decode", "verdicts_from_rows"]


def verdicts_from_rows(pack_rows: list[dict[str, Any]]) -> dict[str, str]:
    """
    GIVEN PACK family rows on the howto domain
    WHEN scoring dual gate
    THEN return {H-PACK: decide_hpack string}.
    """
    return {"H-PACK": verdict_pack(means_decode(pack_rows))}
