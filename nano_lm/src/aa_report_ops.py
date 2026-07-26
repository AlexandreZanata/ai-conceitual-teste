"""Wave AA REPORT: public closeout gate (product = wrap+bank; not open chat)."""

from __future__ import annotations

from typing import Mapping, Sequence

__all__ = [
    "AA_ID",
    "AA_THESIS",
    "AA_EVIDENCE",
    "AA_REPORT_MARKERS",
    "decide_aa_report",
    "report_markers_ok",
]

AA_ID = "AA-REPORT"
AA_THESIS = (
    "Known-ask product = H-ZWRAP+H-WRAPBANK; paraphrase brittle; "
    "open decode HOLD; preference KILL; DEPL docs synced"
)

AA_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/formal-hwrapbank-wrapbank.md",
    "docs/results/nano-lm/formal-hpara-para.md",
    "docs/results/nano-lm/formal-hservealign-servealign.md",
    "docs/results/nano-lm/formal-hzpref-zpref.md",
    "docs/results/nano-lm/formal-hdepldoc-depl-doc.md",
    "docs/results/nano-lm/wave-z-depl-y.md",
    "docs/results/nano-lm/wave-aa-summary.md",
    "docs/results/nano-lm/paper-lab-wave-aa.md",
    "docs/results/nano-lm/RECIPES.md",
    "docs/results/nano-lm/champion-card.md",
)

AA_REPORT_MARKERS: tuple[str, ...] = (
    "COMPLETE",
    "H-ZWRAP",
    "H-WRAPBANK",
    "H-PARA",
    "H-SERVEALIGN",
    "H-ZPREF",
    "H-DEPL-DOC",
    "HOLD",
    "KILL",
    "PROMOTE",
    "WRAP_LOOKUP",
)


def decide_aa_report(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = AA_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for AA report evidence
    WHEN deciding AA-REPORT
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({AA_ID}: {AA_THESIS})"


def report_markers_ok(
    text: str, *, markers: Sequence[str] = AA_REPORT_MARKERS
) -> bool:
    """
    GIVEN wave-aa-summary body
    WHEN checking closeout markers
    THEN True iff every required marker appears.
    """
    body = str(text)
    return all(m in body for m in markers)
