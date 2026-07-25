"""Aggregate H-XFER2 PACK (+ optional BPACK) rows into dual-gate verdicts."""

from __future__ import annotations

from typing import Any

from xfer_score import means_decode
from xfer2_ops import verdict_bpack, verdict_pack

__all__ = ["means_decode", "verdicts_from_rows"]


def verdicts_from_rows(
    *,
    pack_by: dict[str, list[dict[str, Any]]],
    bpack_by: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, dict[str, str]]:
    """
    GIVEN PACK rows keyed by transfer pack (optional BPACK)
    WHEN scoring dual gates
    THEN return nested verdict strings for decide_hxfer2.
    """
    out: dict[str, dict[str, str]] = {"H-PACK": {}}
    for pack, rows in pack_by.items():
        out["H-PACK"][pack] = verdict_pack(means_decode(rows))
    if bpack_by:
        out["H-BPACK"] = {}
        for pack, rows in bpack_by.items():
            out["H-BPACK"][pack] = verdict_bpack(means_decode(rows))
    return out
