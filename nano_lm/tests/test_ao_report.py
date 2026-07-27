"""Contract: Wave AO REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ao_report_ops import (
    AO_EVIDENCE,
    AO_HITL_SCOREBOARD,
    AO_ID,
    AO_REPORT_MARKERS,
    AO_THESIS,
    antifp_section_ok,
    decide_ao_report,
    render_paper_lab_wave_ao,
    render_wave_ao_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AO7 AO-REPORT
    assert AO_ID == "AO-REPORT"
    assert "not open chat" in AO_THESIS.lower()
    assert "peak" in AO_THESIS.lower() or "dual-arm" in AO_THESIS.lower()
    assert len(AO_EVIDENCE) >= 10
    assert any(r["id"] == "AO-HITL-10" for r in AO_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENCORE" for r in AO_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CTXCORE" for r in AO_HITL_SCOREBOARD)
    assert "FIX" in AO_REPORT_MARKERS
    assert "H-CTXCORE" in AO_REPORT_MARKERS
    assert "anti-FP" in AO_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AO_EVIDENCE}
    out = decide_ao_report(ok)
    assert out.startswith("PROMOTE")
    assert AO_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AO_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ao-summary.md"
    ok[miss] = False
    out = decide_ao_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ao_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTCORE**" in body
    assert "**AO-HITL-10**" in body
    assert "**H-GENCORE**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXCORE only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ao()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AO-HITL-10" in body
    assert "H-CTXCORE" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
