"""Contract: Wave AP REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ap_report_ops import (
    AP_EVIDENCE,
    AP_HITL_SCOREBOARD,
    AP_ID,
    AP_REPORT_MARKERS,
    AP_THESIS,
    antifp_section_ok,
    decide_ap_report,
    render_paper_lab_wave_ap,
    render_wave_ap_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AP7 AP-REPORT
    assert AP_ID == "AP-REPORT"
    assert "not open chat" in AP_THESIS.lower()
    assert "peak" in AP_THESIS.lower() or "dual-arm" in AP_THESIS.lower()
    assert len(AP_EVIDENCE) >= 10
    assert any(r["id"] == "AP-HITL-10" for r in AP_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENBASE" for r in AP_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CTXBASE" for r in AP_HITL_SCOREBOARD)
    assert "FIX" in AP_REPORT_MARKERS
    assert "H-CTXBASE" in AP_REPORT_MARKERS
    assert "anti-FP" in AP_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AP_EVIDENCE}
    out = decide_ap_report(ok)
    assert out.startswith("PROMOTE")
    assert AP_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AP_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ap-summary.md"
    ok[miss] = False
    out = decide_ap_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ap_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTBASE**" in body
    assert "**AP-HITL-10**" in body
    assert "**H-GENBASE**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXBASE only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ap()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AP-HITL-10" in body
    assert "H-CTXBASE" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
