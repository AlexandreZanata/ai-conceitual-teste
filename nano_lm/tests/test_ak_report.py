"""Contract: Wave AK REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ak_report_ops import (
    AK_EVIDENCE,
    AK_HITL_SCOREBOARD,
    AK_ID,
    AK_REPORT_MARKERS,
    AK_THESIS,
    antifp_section_ok,
    decide_ak_report,
    render_paper_lab_wave_ak,
    render_wave_ak_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AK7 AK-REPORT
    assert AK_ID == "AK-REPORT"
    assert "not open chat" in AK_THESIS.lower()
    assert "peak" in AK_THESIS.lower() or "dual-arm" in AK_THESIS.lower()
    assert len(AK_EVIDENCE) >= 10
    assert any(r["id"] == "AK-HITL-10" for r in AK_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENTRUE" for r in AK_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CTXMORE" for r in AK_HITL_SCOREBOARD)
    assert "FIX" in AK_REPORT_MARKERS
    assert "H-CTXMORE" in AK_REPORT_MARKERS
    assert "anti-FP" in AK_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AK_EVIDENCE}
    out = decide_ak_report(ok)
    assert out.startswith("PROMOTE")
    assert AK_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AK_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ak-summary.md"
    ok[miss] = False
    out = decide_ak_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ak_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTMORE**" in body
    assert "**AK-HITL-10**" in body
    assert "**H-GENTRUE**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXMORE only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ak()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AK-HITL-10" in body
    assert "H-CTXMORE" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
