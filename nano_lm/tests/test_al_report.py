"""Contract: Wave AL REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from al_report_ops import (
    AL_EVIDENCE,
    AL_HITL_SCOREBOARD,
    AL_ID,
    AL_REPORT_MARKERS,
    AL_THESIS,
    antifp_section_ok,
    decide_al_report,
    render_paper_lab_wave_al,
    render_wave_al_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AL7 AL-REPORT
    assert AL_ID == "AL-REPORT"
    assert "not open chat" in AL_THESIS.lower()
    assert "peak" in AL_THESIS.lower() or "dual-arm" in AL_THESIS.lower()
    assert len(AL_EVIDENCE) >= 10
    assert any(r["id"] == "AL-HITL-10" for r in AL_HITL_SCOREBOARD)
    assert any(r["id"] == "H-GENFRESH" for r in AL_HITL_SCOREBOARD)
    assert any(r["id"] == "H-CTXFRESH" for r in AL_HITL_SCOREBOARD)
    assert "FIX" in AL_REPORT_MARKERS
    assert "H-CTXFRESH" in AL_REPORT_MARKERS
    assert "anti-FP" in AL_REPORT_MARKERS


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AL_EVIDENCE}
    out = decide_al_report(ok)
    assert out.startswith("PROMOTE")
    assert AL_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AL_EVIDENCE}
    miss = "docs/results/nano-lm/wave-al-summary.md"
    ok[miss] = False
    out = decide_al_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_al_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-FASTFRESH**" in body
    assert "**AL-HITL-10**" in body
    assert "**H-GENFRESH**" in body
    assert "FIX count" in body
    assert "Lookup mean" in body
    assert "Gen mean" in body
    assert "not generative IQ" in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("CTXFRESH only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_al()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AL-HITL-10" in body
    assert "H-CTXFRESH" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
