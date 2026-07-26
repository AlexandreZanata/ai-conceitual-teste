"""Contract: Wave AF REPORT closeout (summary + paper-lab + FIX log)."""

from __future__ import annotations

from af_report_ops import (
    AF_EVIDENCE,
    AF_HITL_SCOREBOARD,
    AF_ID,
    AF_REPORT_MARKERS,
    AF_THESIS,
    decide_af_report,
    render_paper_lab_wave_af,
    render_wave_af_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF6 AF-REPORT
    assert AF_ID == "AF-REPORT"
    assert "not open chat" in AF_THESIS.lower()
    assert len(AF_EVIDENCE) >= 10
    assert any(r["id"] == "AF-HITL-10" for r in AF_HITL_SCOREBOARD)
    assert "FIX" in AF_REPORT_MARKERS
    assert "H-CTXULTRA" in AF_REPORT_MARKERS
    assert "H-APPULTRA" in AF_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AF_EVIDENCE}
    out = decide_af_report(ok)
    assert out.startswith("PROMOTE")
    assert AF_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AF_EVIDENCE}
    miss = "docs/results/nano-lm/wave-af-summary.md"
    ok[miss] = False
    out = decide_af_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_af_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert "**H-FASTULTRA**" in body
    assert "**AF-HITL-10**" in body
    assert "FIX count" in body
    assert "**7**" in body  # APPULTRA OOS FIX count


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXULTRA only") is False
    assert scoreboard_ok("no table") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_af()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AF-HITL-10" in body
    assert "H-CTXULTRA" in body
    assert "H-APPULTRA" in body
