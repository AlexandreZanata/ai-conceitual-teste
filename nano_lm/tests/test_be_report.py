"""Contract: Wave BE REPORT closeout (summary + paper-lab + anti-FP · util)."""

from __future__ import annotations

from be_report_ops import (
    BE_EVIDENCE,
    BE_ID,
    BE_REPORT_MARKERS,
    BE_SCOREBOARD,
    BE_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_be_report,
    realeval_section_ok,
    render_paper_lab_wave_be,
    render_wave_be_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_be7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BE7 BE-REPORT
    assert BE_ID == "BE-REPORT"
    assert "not unlabeled open chat" in BE_THESIS.lower()
    assert "NANOGEN15" in BE_THESIS
    assert "DEFER" in BE_THESIS
    assert "COMPINT" in BE_THESIS
    assert "SHIPUSE" in BE_THESIS
    assert "FASTBE" in BE_THESIS
    assert "CTXBE" in BE_THESIS
    assert "BE-FOREVER" in BE_THESIS or "forever" in BE_THESIS.lower()
    assert len(BE_EVIDENCE) >= 8
    assert any(r["id"] == "BE-REAL-EVAL" for r in BE_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN15" and r["decision"] == "DEFER"
        for r in BE_SCOREBOARD
    )
    assert any(r["id"] == "H-COMPINT" for r in BE_SCOREBOARD)
    assert any(r["id"] == "H-SHIPUSE" for r in BE_SCOREBOARD)
    assert "H-CTXBE" in BE_REPORT_MARKERS
    assert "anti-FP" in BE_REPORT_MARKERS
    assert "ABSTAIN" in BE_REPORT_MARKERS
    assert "span-fallback" in BE_REPORT_MARKERS
    assert "true_continue" in BE_REPORT_MARKERS
    assert "BE-FOREVER" in BE_REPORT_MARKERS
    assert "over-refuse" in BE_REPORT_MARKERS
    assert "utilization" in BE_REPORT_MARKERS
    assert "H-NANOGEN6" in BE_REPORT_MARKERS
    assert "H-NANOGEN14" in BE_REPORT_MARKERS
    assert "H-NANOGEN15" in BE_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BE_EVIDENCE}
    out = decide_be_report(ok)
    assert out.startswith("PROMOTE")
    assert BE_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BE_EVIDENCE}
    miss = "docs/results/nano-lm/wave-be-summary.md"
    ok[miss] = False
    out = decide_be_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_be_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-COMPINT**" in body
    assert "**H-SHIPUSE**" in body
    assert "**H-NANOGEN15**" in body
    assert "**H-NANOGEN14**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BE-REAL-EVAL**" in body
    assert "BE-FOREVER" in body
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
    assert "utilization" in body.lower()
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_be()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BE-REAL-EVAL" in body
    assert "H-NANOGEN15" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN14" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "BE-FOREVER" in body
    assert "over-refuse" in body.lower()
    assert "utilization" in body.lower() or "util" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
