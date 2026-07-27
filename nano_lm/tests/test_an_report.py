"""Contract: Wave AN REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from an_report_ops import (
    AN_EVIDENCE,
    AN_HITL_SCOREBOARD,
    AN_ID,
    AN_REPORT_MARKERS,
    AN_THESIS,
    antifp_section_ok,
    decide_an_report,
    render_paper_lab_wave_an,
    render_wave_an_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AN7 AN-REPORT
    assert AN_ID == "AN-REPORT"
    assert "not open chat" in AN_THESIS.lower()
    assert "peak" in AN_THESIS.lower() or "dual-arm" in AN_THESIS.lower()
    assert len(AN_EVIDENCE) >= 10
    assert any(r["id"] == "AN-HITL-10" for r in AN_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENEDGE" for r in AN_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CTXEDGE" for r in AN_HITL_SCOREBOARD)
    assert "FIX" in AN_REPORT_MARKERS
    assert "H-CTXEDGE" in AN_REPORT_MARKERS
    assert "anti-FP" in AN_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AN_EVIDENCE}
    out = decide_an_report(ok)
    assert out.startswith("PROMOTE")
    assert AN_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AN_EVIDENCE}
    miss = "docs/results/nano-lm/wave-an-summary.md"
    ok[miss] = False
    out = decide_an_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_an_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTEDGE**" in body
    assert "**AN-HITL-10**" in body
    assert "**H-GENEDGE**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXEDGE only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_an()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AN-HITL-10" in body
    assert "H-CTXEDGE" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
