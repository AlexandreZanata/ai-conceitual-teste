"""Contract: Wave AV REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from av_report_ops import (
    AV_EVIDENCE,
    AV_ID,
    AV_REPORT_MARKERS,
    AV_SCOREBOARD,
    AV_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_av_report,
    realeval_section_ok,
    render_paper_lab_wave_av,
    render_wave_av_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_av5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AV5 AV-REPORT
    assert AV_ID == "AV-REPORT"
    assert "not unlabeled open chat" in AV_THESIS.lower()
    assert "NANOGEN6" in AV_THESIS
    assert "HOLD" in AV_THESIS
    assert "PRODSHIP" in AV_THESIS
    assert "SHIPUI2" in AV_THESIS
    assert len(AV_EVIDENCE) >= 8
    assert any(r["id"] == "AV-REAL-EVAL" for r in AV_SCOREBOARD)
    assert any(r["id"] == "H-NANOGEN6" and r["decision"] == "HOLD" for r in AV_SCOREBOARD)
    assert any(r["id"] == "H-PRODSHIP" for r in AV_SCOREBOARD)
    assert "H-SHIPUI2" in AV_REPORT_MARKERS
    assert "anti-FP" in AV_REPORT_MARKERS
    assert "ABSTAIN" in AV_REPORT_MARKERS
    assert "span-fallback" in AV_REPORT_MARKERS
    assert "true_continue" in AV_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AV_EVIDENCE}
    out = decide_av_report(ok)
    assert out.startswith("PROMOTE")
    assert AV_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AV_EVIDENCE}
    miss = "docs/results/nano-lm/wave-av-summary.md"
    ok[miss] = False
    out = decide_av_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_av_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODSHIP**" in body
    assert "**H-NANOGEN6**" in body
    assert "**AV-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "HOLD" in body
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_av()
    assert "COMPLETE" in body and "FROZEN" in body
    assert "not unlabeled open chat" in body
    assert "AV-REAL-EVAL" in body
    assert "H-NANOGEN6" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
