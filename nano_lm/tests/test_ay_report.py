"""Contract: Wave AY REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ay_report_ops import (
    AY_EVIDENCE,
    AY_ID,
    AY_REPORT_MARKERS,
    AY_SCOREBOARD,
    AY_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_ay_report,
    realeval_section_ok,
    render_paper_lab_wave_ay,
    render_wave_ay_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_ay5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AY5 AY-REPORT
    assert AY_ID == "AY-REPORT"
    assert "not unlabeled open chat" in AY_THESIS.lower()
    assert "NANOGEN9" in AY_THESIS
    assert "DEFER" in AY_THESIS
    assert "PRODINT" in AY_THESIS
    assert "SHIPAY" in AY_THESIS
    assert "NANOGEN8" in AY_THESIS or "NANOGEN8" in AY_REPORT_MARKERS
    assert "NANOGEN6" in AY_THESIS or "NANOGEN6" in AY_REPORT_MARKERS
    assert "NANOGEN7" in AY_THESIS or "NANOGEN7" in AY_REPORT_MARKERS
    assert len(AY_EVIDENCE) >= 8
    assert any(r["id"] == "AY-REAL-EVAL" for r in AY_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN9" and r["decision"] == "DEFER"
        for r in AY_SCOREBOARD
    )
    assert any(r["id"] == "H-PRODINT" for r in AY_SCOREBOARD)
    assert "H-SHIPAY" in AY_REPORT_MARKERS
    assert "anti-FP" in AY_REPORT_MARKERS
    assert "ABSTAIN" in AY_REPORT_MARKERS
    assert "span-fallback" in AY_REPORT_MARKERS
    assert "true_continue" in AY_REPORT_MARKERS
    assert "intent" in AY_REPORT_MARKERS
    assert "H-NANOGEN6" in AY_REPORT_MARKERS
    assert "H-NANOGEN7" in AY_REPORT_MARKERS
    assert "H-NANOGEN8" in AY_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AY_EVIDENCE}
    out = decide_ay_report(ok)
    assert out.startswith("PROMOTE")
    assert AY_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AY_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ay-summary.md"
    ok[miss] = False
    out = decide_ay_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ay_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODINT**" in body
    assert "**H-NANOGEN9**" in body
    assert "**H-NANOGEN8**" in body
    assert "**H-NANOGEN6**" in body
    assert "**H-NANOGEN7**" in body
    assert "**AY-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "DEFER" in body
    assert "HOLD" in body
    assert "intent" in body.lower()
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ay()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "AY-REAL-EVAL" in body
    assert "H-NANOGEN9" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN7" in body
    assert "H-NANOGEN8" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "intent" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
