"""Contract: Wave AR REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ar_report_ops import (
    AR_EVIDENCE,
    AR_ID,
    AR_REPORT_MARKERS,
    AR_SCOREBOARD,
    AR_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_ar_report,
    render_paper_lab_wave_ar,
    render_wave_ar_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_ar7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR7 AR-REPORT
    assert AR_ID == "AR-REPORT"
    assert "not open chat" in AR_THESIS.lower()
    assert "HOLD" in AR_THESIS
    assert "NANOGEN2" in AR_THESIS
    assert len(AR_EVIDENCE) >= 10
    assert any(r["id"] == "AR-DUAL-HITL" for r in AR_SCOREBOARD)
    assert any(r["id"] == "H-NANOGEN2" for r in AR_SCOREBOARD)
    assert any(r["id"] == "H-ABSTAIN" for r in AR_SCOREBOARD)
    assert "H-SHIPDEMO" in AR_REPORT_MARKERS
    assert "anti-FP" in AR_REPORT_MARKERS
    assert "ABSTAIN" in AR_REPORT_MARKERS
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AR_EVIDENCE}
    out = decide_ar_report(ok)
    assert out.startswith("PROMOTE")
    assert AR_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AR_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ar-summary.md"
    ok[miss] = False
    out = decide_ar_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ar_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert "**H-ABSTAIN**" in body
    assert "**H-NANOGEN2**" in body
    assert "**AR-DUAL-HITL**" in body
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
    body = render_paper_lab_wave_ar()
    assert "COMPLETE" in body and "FROZEN" in body
    assert "not open chat" in body
    assert "AR-DUAL-HITL" in body
    assert "H-NANOGEN2" in body
    assert "HOLD" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "product layer" in body
    assert "≤5M" in body or "5M" in body
