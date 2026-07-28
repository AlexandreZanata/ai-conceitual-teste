"""Contract: Wave BB REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from bb_report_ops import (
    BB_EVIDENCE,
    BB_ID,
    BB_REPORT_MARKERS,
    BB_SCOREBOARD,
    BB_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bb_report,
    realeval_section_ok,
    render_paper_lab_wave_bb,
    render_wave_bb_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_bb6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8 BB6 BB-REPORT
    assert BB_ID == "BB-REPORT"
    assert "not unlabeled open chat" in BB_THESIS.lower()
    assert "NANOGEN12" in BB_THESIS
    assert "DEFER" in BB_THESIS
    assert "INTENTGEN" in BB_THESIS
    assert "FASTHOLD" in BB_THESIS
    assert "CTXHOLD" in BB_THESIS
    assert "BB-FOREVER" in BB_THESIS or "forever" in BB_THESIS.lower()
    assert len(BB_EVIDENCE) >= 8
    assert any(r["id"] == "BB-REAL-EVAL" for r in BB_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN12" and r["decision"] == "DEFER"
        for r in BB_SCOREBOARD
    )
    assert any(r["id"] == "H-INTENTGEN" for r in BB_SCOREBOARD)
    assert "H-CTXHOLD" in BB_REPORT_MARKERS
    assert "anti-FP" in BB_REPORT_MARKERS
    assert "ABSTAIN" in BB_REPORT_MARKERS
    assert "span-fallback" in BB_REPORT_MARKERS
    assert "true_continue" in BB_REPORT_MARKERS
    assert "BB-FOREVER" in BB_REPORT_MARKERS
    assert "over-refuse" in BB_REPORT_MARKERS
    assert "H-NANOGEN6" in BB_REPORT_MARKERS
    assert "H-NANOGEN11" in BB_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BB_EVIDENCE}
    out = decide_bb_report(ok)
    assert out.startswith("PROMOTE")
    assert BB_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BB_EVIDENCE}
    miss = "docs/results/nano-lm/wave-bb-summary.md"
    ok[miss] = False
    out = decide_bb_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_bb_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-INTENTGEN**" in body
    assert "**H-NANOGEN12**" in body
    assert "**H-NANOGEN11**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BB-REAL-EVAL**" in body
    assert "BB-FOREVER" in body
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
    body = render_paper_lab_wave_bb()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BB-REAL-EVAL" in body
    assert "H-NANOGEN12" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN11" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "BB-FOREVER" in body
    assert "over-refuse" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
