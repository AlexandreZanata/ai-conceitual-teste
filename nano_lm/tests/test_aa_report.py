"""Contract: Wave AA REPORT closeout gate (public summary + paper-lab)."""

from __future__ import annotations

from aa_report_ops import (
    AA_EVIDENCE,
    AA_ID,
    AA_REPORT_MARKERS,
    AA_THESIS,
    decide_aa_report,
    report_markers_ok,
)


def test_given_all_evidence_when_decide_then_promote() -> None:
    # GIVEN/WHEN/THEN: Wave AA closeout like Z6 — all public evidence present
    ok = {p: True for p in AA_EVIDENCE}
    out = decide_aa_report(ok)
    assert out.startswith("PROMOTE")
    assert AA_ID in out
    assert "H-ZWRAP" in AA_THESIS or "WRAPBANK" in AA_THESIS


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AA_EVIDENCE}
    miss = "docs/results/nano-lm/wave-aa-summary.md"
    ok[miss] = False
    out = decide_aa_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_thesis_text_when_markers_then_ok() -> None:
    body = (
        "Wave AA COMPLETE. Product remains H-ZWRAP WRAP_LOOKUP plus H-WRAPBANK. "
        "H-PARA HOLD brittleness; H-SERVEALIGN HOLD open decode; H-ZPREF KILL; "
        "H-DEPL-DOC PROMOTE. Not an open chat LM."
    )
    assert report_markers_ok(body) is True
    assert "H-WRAPBANK" in AA_REPORT_MARKERS


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("WRAPBANK only") is False


def test_given_constants_when_loaded_then_match_wave() -> None:
    assert AA_ID == "AA-REPORT"
    assert len(AA_EVIDENCE) >= 8
    assert "COMPLETE" in AA_REPORT_MARKERS
