"""Contract: Wave BA REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ba_report_ops import (
    BA_EVIDENCE,
    BA_ID,
    BA_REPORT_MARKERS,
    BA_SCOREBOARD,
    BA_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_ba_report,
    realeval_section_ok,
    render_paper_lab_wave_ba,
    render_wave_ba_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_ba6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BA6 BA-REPORT
    assert BA_ID == "BA-REPORT"
    assert "not unlabeled open chat" in BA_THESIS.lower()
    assert "NANOGEN11" in BA_THESIS
    assert "DEFER" in BA_THESIS
    assert "REALGAIN" in BA_THESIS
    assert "FASTREAL" in BA_THESIS
    assert "CTXREAL2" in BA_THESIS
    assert "forever" in BA_THESIS.lower()
    assert len(BA_EVIDENCE) >= 8
    assert any(r["id"] == "BA-REAL-EVAL" for r in BA_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN11" and r["decision"] == "DEFER"
        for r in BA_SCOREBOARD
    )
    assert any(r["id"] == "H-REALGAIN" for r in BA_SCOREBOARD)
    assert "H-CTXREAL2" in BA_REPORT_MARKERS
    assert "anti-FP" in BA_REPORT_MARKERS
    assert "ABSTAIN" in BA_REPORT_MARKERS
    assert "span-fallback" in BA_REPORT_MARKERS
    assert "true_continue" in BA_REPORT_MARKERS
    assert "forever" in BA_REPORT_MARKERS
    assert "over-refuse" in BA_REPORT_MARKERS
    assert "H-NANOGEN6" in BA_REPORT_MARKERS
    assert "H-NANOGEN10" in BA_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BA_EVIDENCE}
    out = decide_ba_report(ok)
    assert out.startswith("PROMOTE")
    assert BA_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BA_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ba-summary.md"
    ok[miss] = False
    out = decide_ba_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ba_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-REALGAIN**" in body
    assert "**H-NANOGEN11**" in body
    assert "**H-NANOGEN10**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BA-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "DEFER" in body
    assert "HOLD" in body
    assert "forever" in body.lower()
    assert "over-refuse" in body.lower()
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ba()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BA-REAL-EVAL" in body
    assert "H-NANOGEN11" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN10" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "forever" in body.lower()
    assert "over-refuse" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
