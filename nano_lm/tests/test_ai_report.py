"""Contract: Wave AI REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ai_report_ops import (
    AI_EVIDENCE,
    AI_HITL_SCOREBOARD,
    AI_ID,
    AI_REPORT_MARKERS,
    AI_THESIS,
    antifp_section_ok,
    decide_ai_report,
    render_paper_lab_wave_ai,
    render_wave_ai_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AI7 AI-REPORT
    assert AI_ID == "AI-REPORT"
    assert "not open chat" in AI_THESIS.lower()
    assert "dual-arm" in AI_THESIS.lower() or "push" in AI_THESIS.lower()
    assert len(AI_EVIDENCE) >= 10
    assert any(r["id"] == "AI-HITL-10" for r in AI_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CAPRENEG" for r in AI_HITL_SCOREBOARD)
    assert "FIX" in AI_REPORT_MARKERS
    assert "H-CTXPUSH" in AI_REPORT_MARKERS
    assert "anti-FP" in AI_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AI_EVIDENCE}
    out = decide_ai_report(ok)
    assert out.startswith("PROMOTE")
    assert AI_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AI_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ai-summary.md"
    ok[miss] = False
    out = decide_ai_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ai_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTPUSH**" in body
    assert "**AI-HITL-10**" in body
    assert "**H-CAPRENEG**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXPUSH only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ai()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AI-HITL-10" in body
    assert "H-CTXPUSH" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
