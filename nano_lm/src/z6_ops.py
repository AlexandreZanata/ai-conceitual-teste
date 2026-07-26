"""Wave Z6 REPORT: public HITL note gate (PFB ≠ interactive LM)."""

from __future__ import annotations

from typing import Mapping, Sequence

__all__ = [
    "Z6_ID",
    "Z6_THESIS",
    "Z6_EVIDENCE",
    "Z6_REPORT_MARKERS",
    "decide_z6",
    "report_markers_ok",
]

Z6_ID = "Z6"
Z6_THESIS = "PFB recipes ≠ interactive LM; wrap + error-bank loop"

Z6_EVIDENCE: tuple[str, ...] = (
    "docs/results/nano-lm/wave-z-export.md",
    "docs/results/nano-lm/wave-z-hitl-z1.md",
    "docs/results/nano-lm/wave-z-hitl-z2.md",
    "docs/results/nano-lm/wave-z-zerr.md",
    "docs/results/nano-lm/wave-z-hitl-z4.md",
    "docs/results/nano-lm/wave-z-depl-y.md",
    "docs/results/nano-lm/wave-z-summary.md",
    "docs/results/nano-lm/wave-z-hitl.md",
    "docs/results/nano-lm/paper-lab-wave-z.md",
)

# Required substrings inside wave-z-hitl.md (honest claims).
Z6_REPORT_MARKERS: tuple[str, ...] = (
    "H-ZWRAP",
    "H-ZERR",
    "WRAP_LOOKUP",
    "period",
    "DEPL-Y",
    "COMPLETE",
    "interactive",
    "error-bank",
    "PFB",
)


def decide_z6(
    evidence_ok: Mapping[str, bool],
    *,
    required: Sequence[str] = Z6_EVIDENCE,
) -> str:
    """
    GIVEN path→exists for Z6 evidence set
    WHEN deciding report gate
    THEN PROMOTE iff every required path exists; else KILL first miss.
    """
    for path in required:
        if not bool(evidence_ok.get(path)):
            return f"KILL (missing evidence: {path})"
    return f"PROMOTE ({Z6_ID}: {Z6_THESIS})"


def report_markers_ok(text: str, *, markers: Sequence[str] = Z6_REPORT_MARKERS) -> bool:
    """
    GIVEN public HITL report body
    WHEN checking thesis markers
    THEN True iff every required marker appears.
    """
    body = str(text)
    return all(m in body for m in markers)
