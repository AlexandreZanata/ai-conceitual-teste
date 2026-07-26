"""Contract: Wave AD REPORT closeout (summary + paper-lab + FIX log)."""

from __future__ import annotations

from ad_report_ops import (
    AD_EVIDENCE,
    AD_HITL_SCOREBOARD,
    AD_ID,
    AD_REPORT_MARKERS,
    AD_THESIS,
    decide_ad_report,
    render_paper_lab_wave_ad,
    render_wave_ad_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.6 / §13 AD6 AD-REPORT
    assert AD_ID == "AD-REPORT"
    assert "not open chat" in AD_THESIS.lower()
    assert len(AD_EVIDENCE) >= 10
    assert any(r["id"] == "AD-HITL-10" for r in AD_HITL_SCOREBOARD)
    assert "FIX" in AD_REPORT_MARKERS
    assert "H-COMPOSE" in AD_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AD_EVIDENCE}
    out = decide_ad_report(ok)
    assert out.startswith("PROMOTE")
    assert AD_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AD_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ad-summary.md"
    ok[miss] = False
    out = decide_ad_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ad_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert "**H-ROUTEPLUS**" in body
    assert "**AD-HITL-10**" in body
    assert "FIX count" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("COMPOSE only") is False
    assert scoreboard_ok("no table") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ad()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AD-HITL-10" in body
    assert "H-HARDPARA" in body
