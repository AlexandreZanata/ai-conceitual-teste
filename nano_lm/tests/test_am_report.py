"""Contract: Wave AM REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from am_report_ops import (
    AM_EVIDENCE,
    AM_HITL_SCOREBOARD,
    AM_ID,
    AM_REPORT_MARKERS,
    AM_THESIS,
    antifp_section_ok,
    decide_am_report,
    render_paper_lab_wave_am,
    render_wave_am_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AM7 AM-REPORT
    assert AM_ID == "AM-REPORT"
    assert "not open chat" in AM_THESIS.lower()
    assert "peak" in AM_THESIS.lower() or "dual-arm" in AM_THESIS.lower()
    assert len(AM_EVIDENCE) >= 10
    assert any(r["id"] == "AM-HITL-10" for r in AM_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENTRUTH" for r in AM_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CTXNEXT" for r in AM_HITL_SCOREBOARD)
    assert "FIX" in AM_REPORT_MARKERS
    assert "H-CTXNEXT" in AM_REPORT_MARKERS
    assert "anti-FP" in AM_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AM_EVIDENCE}
    out = decide_am_report(ok)
    assert out.startswith("PROMOTE")
    assert AM_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AM_EVIDENCE}
    miss = "docs/results/nano-lm/wave-am-summary.md"
    ok[miss] = False
    out = decide_am_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_am_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTNEXT**" in body
    assert "**AM-HITL-10**" in body
    assert "**H-GENTRUTH**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXNEXT only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_am()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AM-HITL-10" in body
    assert "H-CTXNEXT" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
