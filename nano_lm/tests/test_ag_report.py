"""Contract: Wave AG REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ag_report_ops import (
    AG_EVIDENCE,
    AG_HITL_SCOREBOARD,
    AG_ID,
    AG_REPORT_MARKERS,
    AG_THESIS,
    antifp_section_ok,
    decide_ag_report,
    render_paper_lab_wave_ag,
    render_wave_ag_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AG7 AG-REPORT
    assert AG_ID == "AG-REPORT"
    assert "not open chat" in AG_THESIS.lower()
    assert "anti-FP" in AG_THESIS or "dual-arm" in AG_THESIS.lower()
    assert len(AG_EVIDENCE) >= 10
    assert any(r["id"] == "AG-HITL-10" for r in AG_HITL_SCOREBOARD)
    assert "FIX" in AG_REPORT_MARKERS
    assert "H-ANTIFP" in AG_REPORT_MARKERS
    assert "anti-FP" in AG_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AG_EVIDENCE}
    out = decide_ag_report(ok)
    assert out.startswith("PROMOTE")
    assert AG_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AG_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ag-summary.md"
    ok[miss] = False
    out = decide_ag_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ag_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTREAL**" in body
    assert "**AG-HITL-10**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ANTIFP only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ag()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AG-HITL-10" in body
    assert "H-ANTIFP" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
