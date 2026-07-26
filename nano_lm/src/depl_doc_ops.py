"""H-DEPL-DOC: public one-pagers must match DEPL-Y (+ Wave AA outcomes)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

__all__ = [
    "DEPL_DOC_ID",
    "ONE_PAGERS",
    "CORE_MARKERS",
    "AA_OUTCOME_MARKERS",
    "missing_markers",
    "page_sync_report",
    "decide_depl_doc",
]

DEPL_DOC_ID = "H-DEPL-DOC"

# Public surfaces that must stay aligned with DEPL-Y (no new hyps).
ONE_PAGERS: tuple[str, ...] = (
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
    "docs/NANO-STUDENT-AGENDA.md",
    "docs/results/nano-lm/wave-z-depl-y.md",
)

# DEPL-Y deploy spine markers (must appear in each one-pager).
CORE_MARKERS: tuple[str, ...] = (
    "DEPL-Y",
    "H-PACK",
    "QPFB2",
    "ROLL",
    "H-ZWRAP",
    "H-ZERR",
)

# Wave AA outcomes that one-pagers must reflect (except depl-y freeze note).
AA_OUTCOME_MARKERS: tuple[tuple[str, str], ...] = (
    ("H-WRAPBANK", "PROMOTE"),
    ("H-PARA", "HOLD"),
    ("H-ZPREF", "KILL"),
)


def missing_markers(text: str, markers: Sequence[str]) -> list[str]:
    """
    GIVEN one-pager body + required substrings
    WHEN scanning
    THEN return markers absent from text.
    """
    body = str(text)
    return [m for m in markers if m not in body]


def _aa_missing(text: str) -> list[str]:
    body = str(text)
    miss: list[str] = []
    for hyp, outcome in AA_OUTCOME_MARKERS:
        if hyp not in body or outcome not in body:
            miss.append(f"{hyp}/{outcome}")
    return miss


def page_sync_report(path: str, text: str) -> dict[str, Any]:
    """
    GIVEN one path + body
    WHEN checking DEPL-DOC sync
    THEN return ok + missing list (AA outcomes waived on wave-z-depl-y.md).
    """
    miss = missing_markers(text, CORE_MARKERS)
    # DEPL-Y freeze page is the policy source; AA outcomes live on card/RECIPES/agenda.
    if not str(path).endswith("wave-z-depl-y.md"):
        miss.extend(_aa_missing(text))
    # Agenda is short: allow DEPL-Y via link text "lab-freeze" + recipes pointer —
    # still require CORE; AA outcomes required.
    return {
        "path": path,
        "ok": len(miss) == 0,
        "missing": miss,
    }


def decide_depl_doc(reports: Sequence[Mapping[str, Any]]) -> str:
    """
    GIVEN per-page sync reports
    WHEN gating H-DEPL-DOC (§8.1 AA4)
    THEN PROMOTE iff every page ok; else KILL naming first gap.
    """
    for rep in reports:
        if not bool(rep.get("ok")):
            miss = rep.get("missing") or ["?"]
            return f"KILL ({rep.get('path')}: missing {miss[0]})"
    return "PROMOTE"
