"""Wave AQ4 H-KBCOV: KB coverage % + explicit hole list (no fake 100%)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from aq_session_ops import AQ0_PRODUCT_HOLES, kb_coverage_snapshot
from z_wrap import lookup_gold

__all__ = [
    "KBCOV_ID",
    "KBCOV_THESIS",
    "PRODUCT_HOLES",
    "build_kbcov_snapshot",
    "parent_gold_hits",
    "curated_blob_stats",
    "decide_kbcov",
]

KBCOV_ID = "H-KBCOV"
PRODUCT_HOLES = AQ0_PRODUCT_HOLES
KBCOV_THESIS = (
    "Publish curated∩bank coverage % + explicit hole list; "
    "never claim complete product KB (no fake 100%)"
)


def build_kbcov_snapshot(
    *,
    curated_ids: set[str],
    bank_source_ids: set[str],
) -> dict[str, object]:
    """
    GIVEN curated registry ids + bank source_ids
    WHEN computing H-KBCOV snapshot
    THEN reuse AQ0 coverage math with product holes always present.
    """
    return dict(
        kb_coverage_snapshot(
            curated_ids=curated_ids, bank_source_ids=bank_source_ids
        )
    )


def parent_gold_hits(
    parents: Sequence[Mapping[str, str]],
    bank_rows: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    """
    GIVEN PARA/parent questions + bank rows
    WHEN checking exact LOOKUP golds
    THEN report hit rate + miss ids (product known-ask coverage).
    """
    hits: list[str] = []
    misses: list[str] = []
    for item in parents:
        tid = str(item.get("id", "")).strip() or "?"
        q = str(item.get("parent_question", item.get("question", "")))
        gold = lookup_gold(q, bank_rows)
        if gold is not None:
            hits.append(tid)
        else:
            misses.append(tid)
    n = len(parents)
    pct = (100.0 * len(hits) / n) if n else 0.0
    return {
        "n": n,
        "hit_n": len(hits),
        "miss_n": len(misses),
        "hit_pct": round(pct, 2),
        "hit_ids": hits,
        "miss_ids": misses,
    }


def curated_blob_stats(
    checks: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    """
    GIVEN per-source curated path checks
    WHEN summarizing blob presence
    THEN present_n / missing ids.
    """
    present = [str(c["source_id"]) for c in checks if bool(c.get("exists"))]
    missing = [
        str(c["source_id"]) for c in checks if not bool(c.get("exists"))
    ]
    n = len(checks)
    pct = (100.0 * len(present) / n) if n else 0.0
    return {
        "n": n,
        "present_n": len(present),
        "missing_n": len(missing),
        "present_pct": round(pct, 2),
        "missing_ids": missing,
    }


def decide_kbcov(
    *,
    snap: Mapping[str, object],
    blobs: Mapping[str, object],
    parents: Mapping[str, object],
) -> str:
    """
    GIVEN coverage snapshot + blob + parent-gold stats
    WHEN applying H-KBCOV gate
    THEN PROMOTE iff % published, product holes explicit, no fake complete.
    """
    if "coverage_pct" not in snap:
        return "KILL (coverage_pct missing)"
    if not bool(snap.get("complete_claim_forbidden")):
        return "KILL (complete_claim_forbidden must be true — no fake 100%)"
    holes = snap.get("holes")
    if not isinstance(holes, list) or len(holes) < 1:
        return "KILL (holes list empty — no fake 100% completeness)"
    for hole in PRODUCT_HOLES:
        if hole not in holes:
            return f"KILL (missing product hole: {hole})"
    if int(blobs.get("missing_n") or 0) > 0:
        miss = blobs.get("missing_ids") or []
        return f"KILL (curated blob missing: {miss})"
    if int(parents.get("n") or 0) < 1:
        return "KILL (parent gold probe empty)"
    # Registry 100% is allowed only with product holes + forbidden complete.
    return "PROMOTE"
