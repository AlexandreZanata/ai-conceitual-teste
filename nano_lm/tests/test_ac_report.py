"""Contract: Wave AC REPORT closeout (summary + paper-lab + FIX log)."""

from __future__ import annotations

from ac_report_ops import (
    AC_EVIDENCE,
    AC_HITL_SCOREBOARD,
    AC_ID,
    AC_REPORT_MARKERS,
    AC_THESIS,
    decide_ac_report,
    render_paper_lab_wave_ac,
    render_wave_ac_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.5 AC6 AC-REPORT
    assert AC_ID == "AC-REPORT"
    assert "not open chat" in AC_THESIS.lower()
    assert len(AC_EVIDENCE) >= 10
    assert any(r["id"] == "AC-HITL-10" for r in AC_HITL_SCOREBOARD)
    assert "FIX" in AC_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AC_EVIDENCE}
    out = decide_ac_report(ok)
    assert out.startswith("PROMOTE")
    assert AC_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AC_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ac-summary.md"
    ok[miss] = False
    out = decide_ac_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ac_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert "**H-APPPLUS**" in body
    assert "**11**" in body  # APPPLUS FIX count


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXPLUS only") is False
    assert scoreboard_ok("no table") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ac()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AC-HITL-10" in body
