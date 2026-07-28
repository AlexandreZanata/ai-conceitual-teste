"""Contract: Wave AZ REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from az_report_ops import (
    AZ_EVIDENCE,
    AZ_ID,
    AZ_REPORT_MARKERS,
    AZ_SCOREBOARD,
    AZ_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_az_report,
    realeval_section_ok,
    render_paper_lab_wave_az,
    render_wave_az_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_az5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AZ5 AZ-REPORT
    assert AZ_ID == "AZ-REPORT"
    assert "not unlabeled open chat" in AZ_THESIS.lower()
    assert "NANOGEN10" in AZ_THESIS
    assert "DEFER" in AZ_THESIS
    assert "PRODGEN" in AZ_THESIS
    assert "SHIPAZ" in AZ_THESIS
    assert "NANOGEN9" in AZ_THESIS or "NANOGEN9" in AZ_REPORT_MARKERS
    assert "NANOGEN6" in AZ_THESIS or "NANOGEN6" in AZ_REPORT_MARKERS
    assert "NANOGEN7" in AZ_THESIS or "NANOGEN7" in AZ_REPORT_MARKERS
    assert len(AZ_EVIDENCE) >= 8
    assert any(r["id"] == "AZ-REAL-EVAL" for r in AZ_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN10" and r["decision"] == "DEFER"
        for r in AZ_SCOREBOARD
    )
    assert any(r["id"] == "H-PRODGEN" for r in AZ_SCOREBOARD)
    assert "H-SHIPAZ" in AZ_REPORT_MARKERS
    assert "anti-FP" in AZ_REPORT_MARKERS
    assert "ABSTAIN" in AZ_REPORT_MARKERS
    assert "span-fallback" in AZ_REPORT_MARKERS
    assert "true_continue" in AZ_REPORT_MARKERS
    assert "held-out" in AZ_REPORT_MARKERS
    assert "over-refuse" in AZ_REPORT_MARKERS
    assert "H-NANOGEN6" in AZ_REPORT_MARKERS
    assert "H-NANOGEN7" in AZ_REPORT_MARKERS
    assert "H-NANOGEN8" in AZ_REPORT_MARKERS
    assert "H-NANOGEN9" in AZ_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AZ_EVIDENCE}
    out = decide_az_report(ok)
    assert out.startswith("PROMOTE")
    assert AZ_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AZ_EVIDENCE}
    miss = "docs/results/nano-lm/wave-az-summary.md"
    ok[miss] = False
    out = decide_az_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_az_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODGEN**" in body
    assert "**H-NANOGEN10**" in body
    assert "**H-NANOGEN9**" in body
    assert "**H-NANOGEN8**" in body
    assert "**H-NANOGEN6**" in body
    assert "**H-NANOGEN7**" in body
    assert "**AZ-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "DEFER" in body
    assert "HOLD" in body
    assert "held-out" in body.lower()
    assert "over-refuse" in body.lower()
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_az()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "AZ-REAL-EVAL" in body
    assert "H-NANOGEN10" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN7" in body
    assert "H-NANOGEN8" in body
    assert "H-NANOGEN9" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "held-out" in body.lower()
    assert "over-refuse" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
