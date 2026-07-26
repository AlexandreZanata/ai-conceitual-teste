"""Contract: Wave AB REPORT closeout (summary + paper-lab + FIX log)."""

from __future__ import annotations

from ab_report_ops import (
    AB_EVIDENCE,
    AB_HITL_SCOREBOARD,
    AB_ID,
    AB_REPORT_MARKERS,
    AB_THESIS,
    decide_ab_report,
    render_paper_lab_wave_ab,
    render_wave_ab_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.3 AB7 AB-REPORT
    assert AB_ID == "AB-REPORT"
    assert "not open chat" in AB_THESIS.lower() or "not open chat LM" in AB_THESIS
    assert len(AB_EVIDENCE) >= 10
    assert any(r["id"] == "AB-HITL-10" for r in AB_HITL_SCOREBOARD)
    assert "FIX" in AB_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AB_EVIDENCE}
    out = decide_ab_report(ok)
    assert out.startswith("PROMOTE")
    assert AB_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AB_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ab-summary.md"
    ok[miss] = False
    out = decide_ab_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ab_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert "**H-ASKSMART**" in body
    assert "**10**" in body  # ASKSMART FIX count


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("SEMWRAP only") is False
    assert scoreboard_ok("no table") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ab()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AB-HITL-10" in body
