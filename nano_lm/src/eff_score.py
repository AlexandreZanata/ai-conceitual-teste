"""Score H-EFF domain PACK rows into family means."""

from __future__ import annotations

from typing import Any

from xfer_score import means_decode

__all__ = ["means_decode", "means_by_domain"]


def means_by_domain(
    domain_rows: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, dict[str, float]]]:
    """
    GIVEN {domain: pack_rows}
    WHEN aggregating
    THEN return {domain: means_decode(rows)}.
    """
    return {name: means_decode(rows) for name, rows in domain_rows.items()}
