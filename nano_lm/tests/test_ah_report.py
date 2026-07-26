"""Contract: Wave AH REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ah_report_ops import (
    AH_EVIDENCE,
    AH_HITL_SCOREBOARD,
    AH_ID,
    AH_REPORT_MARKERS,
    AH_THESIS,
    antifp_section_ok,
    decide_ah_report,
    render_paper_lab_wave_ah,
    render_wave_ah_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AH7 AH-REPORT
    assert AH_ID == "AH-REPORT"
    assert "not open chat" in AH_THESIS.lower()
    assert "dual-arm" in AH_THESIS.lower() or "lift" in AH_THESIS.lower()
    assert len(AH_EVIDENCE) >= 10
    assert any(r["id"] == "AH-HITL-10" for r in AH_HITL_SCOREBOARD)
    assert "FIX" in AH_REPORT_MARKERS
    assert "H-CTXLIFT" in AH_REPORT_MARKERS
    assert "anti-FP" in AH_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AH_EVIDENCE}
    out = decide_ah_report(ok)
    assert out.startswith("PROMOTE")
    assert AH_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AH_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ah-summary.md"
    ok[miss] = False
    out = decide_ah_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ah_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTLIFT**" in body
    assert "**AH-HITL-10**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXLIFT only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ah()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AH-HITL-10" in body
    assert "H-CTXLIFT" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
