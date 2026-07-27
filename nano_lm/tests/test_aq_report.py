"""Contract: Wave AQ REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from aq_report_ops import (
    AQ_EVIDENCE,
    AQ_ID,
    AQ_REPORT_MARKERS,
    AQ_SCOREBOARD,
    AQ_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_aq_report,
    render_paper_lab_wave_aq,
    render_wave_aq_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AQ8 AQ-REPORT
    assert AQ_ID == "AQ-REPORT"
    assert "not open chat" in AQ_THESIS.lower()
    assert "product" in AQ_THESIS.lower()
    assert "HOLD" in AQ_THESIS
    assert "NANOGEN" in AQ_THESIS or "H-NANOGEN" in AQ_THESIS
    assert len(AQ_EVIDENCE) >= 10
    assert any(r["id"] == "AQ-PRODUCT-HITL" for r in AQ_SCOREBOARD)
    assert any(r["id"] == "H-NANOGEN" for r in AQ_SCOREBOARD)
    assert any(r["id"] == "H-PARAHIT" for r in AQ_SCOREBOARD)
    assert "H-MODEUI" in AQ_REPORT_MARKERS
    assert "anti-FP" in AQ_REPORT_MARKERS
    assert "peak_only_lift" in AQ_REPORT_MARKERS
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AQ_EVIDENCE}
    out = decide_aq_report(ok)
    assert out.startswith("PROMOTE")
    assert AQ_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AQ_EVIDENCE}
    miss = "docs/results/nano-lm/wave-aq-summary.md"
    ok[miss] = False
    out = decide_aq_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_aq_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-PARAHIT**" in body
    assert "**H-NANOGEN**" in body
    assert "**AQ-PRODUCT-HITL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("PARAHIT only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_aq()
    assert "COMPLETE" in body
    assert "not open chat" in body
    assert "AQ-PRODUCT-HITL" in body
    assert "H-NANOGEN" in body
    assert "HOLD" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "product layer" in body
    assert "≤5M" in body or "5M" in body
