"""Contract: Wave AJ REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from aj_report_ops import (
    AJ_EVIDENCE,
    AJ_HITL_SCOREBOARD,
    AJ_ID,
    AJ_REPORT_MARKERS,
    AJ_THESIS,
    antifp_section_ok,
    decide_aj_report,
    render_paper_lab_wave_aj,
    render_wave_aj_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AJ7 AJ-REPORT
    assert AJ_ID == "AJ-REPORT"
    assert "not open chat" in AJ_THESIS.lower()
    assert "peak" in AJ_THESIS.lower() or "dual-arm" in AJ_THESIS.lower()
    assert len(AJ_EVIDENCE) >= 10
    assert any(r["id"] == "AJ-HITL-10" for r in AJ_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENPEAK" for r in AJ_HITL_SCOREBOARD)
    assert "FIX" in AJ_REPORT_MARKERS
    assert "H-CTXPEAK" in AJ_REPORT_MARKERS
    assert "anti-FP" in AJ_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AJ_EVIDENCE}
    out = decide_aj_report(ok)
    assert out.startswith("PROMOTE")
    assert AJ_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AJ_EVIDENCE}
    miss = "docs/results/nano-lm/wave-aj-summary.md"
    ok[miss] = False
    out = decide_aj_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_aj_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTPEAK**" in body
    assert "**AJ-HITL-10**" in body
    assert "**H-GENPEAK**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXPEAK only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_aj()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AJ-HITL-10" in body
    assert "H-CTXPEAK" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
