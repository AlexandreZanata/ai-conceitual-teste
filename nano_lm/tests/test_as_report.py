"""Contract: Wave AS REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from as_report_ops import (
    AS_EVIDENCE,
    AS_ID,
    AS_REPORT_MARKERS,
    AS_SCOREBOARD,
    AS_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_as_report,
    render_paper_lab_wave_as,
    render_wave_as_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_as9_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AS9 AS-REPORT
    assert AS_ID == "AS-REPORT"
    assert "not open chat" in AS_THESIS.lower()
    assert "HOLD" in AS_THESIS
    assert "NANOGEN3" in AS_THESIS
    assert len(AS_EVIDENCE) >= 12
    assert any(r["id"] == "AS-DUAL-HITL" for r in AS_SCOREBOARD)
    assert any(r["id"] == "H-NANOGEN3" for r in AS_SCOREBOARD)
    assert any(r["id"] == "H-ASKABSTAIN" for r in AS_SCOREBOARD)
    assert "H-SHIPUI" in AS_REPORT_MARKERS
    assert "anti-FP" in AS_REPORT_MARKERS
    assert "ABSTAIN" in AS_REPORT_MARKERS
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AS_EVIDENCE}
    out = decide_as_report(ok)
    assert out.startswith("PROMOTE")
    assert AS_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AS_EVIDENCE}
    miss = "docs/results/nano-lm/wave-as-summary.md"
    ok[miss] = False
    out = decide_as_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_as_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-ASKABSTAIN**" in body
    assert "**H-NANOGEN3**" in body
    assert "**AS-DUAL-HITL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "Real-eval" in body or "real-eval" in body.lower()
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_as()
    assert "COMPLETE" in body and "FROZEN" in body
    assert "not open chat" in body
    assert "AS-DUAL-HITL" in body
    assert "H-NANOGEN3" in body
    assert "HOLD" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "product layer" in body
    assert "≤5M" in body or "5M" in body
