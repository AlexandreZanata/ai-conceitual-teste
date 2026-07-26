"""Contract: Wave AE REPORT closeout (summary + paper-lab + FIX log)."""

from __future__ import annotations

from ae_report_ops import (
    AE_EVIDENCE,
    AE_HITL_SCOREBOARD,
    AE_ID,
    AE_REPORT_MARKERS,
    AE_THESIS,
    decide_ae_report,
    render_paper_lab_wave_ae,
    render_wave_ae_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE6 AE-REPORT
    assert AE_ID == "AE-REPORT"
    assert "not open chat" in AE_THESIS.lower()
    assert len(AE_EVIDENCE) >= 10
    assert any(r["id"] == "AE-HITL-10" for r in AE_HITL_SCOREBOARD)
    assert "FIX" in AE_REPORT_MARKERS
    assert "H-CTXMAX" in AE_REPORT_MARKERS
    assert "H-APPMAX" in AE_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AE_EVIDENCE}
    out = decide_ae_report(ok)
    assert out.startswith("PROMOTE")
    assert AE_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AE_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ae-summary.md"
    ok[miss] = False
    out = decide_ae_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ae_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert "**H-FASTMAX**" in body
    assert "**AE-HITL-10**" in body
    assert "FIX count" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXMAX only") is False
    assert scoreboard_ok("no table") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ae()
    assert "COMPLETE" in body
    assert "FROZEN" in body or "Freeze" in body
    assert "not open chat" in body
    assert "AE-HITL-10" in body
    assert "H-CTXMAX" in body
    assert "H-APPMAX" in body
