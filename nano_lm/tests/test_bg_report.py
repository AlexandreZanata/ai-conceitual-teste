"""Contract: Wave BG REPORT closeout (summary + paper-lab + anti-FP · util)."""

from __future__ import annotations

from bg_report_ops import (
    BG_EVIDENCE,
    BG_ID,
    BG_REPORT_MARKERS,
    BG_SCOREBOARD,
    BG_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bg_report,
    realeval_section_ok,
    render_paper_lab_wave_bg,
    render_wave_bg_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_bg7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BG7 BG-REPORT
    assert BG_ID == "BG-REPORT"
    assert "not unlabeled open chat" in BG_THESIS.lower()
    assert "NANOGEN17" in BG_THESIS
    assert "SKIP" in BG_THESIS
    assert "UNARYINT" in BG_THESIS
    assert "SHIPPUB" in BG_THESIS
    assert "FASTBG" in BG_THESIS
    assert "CTXBG" in BG_THESIS
    assert "BG-FOREVER" in BG_THESIS or "forever" in BG_THESIS.lower()
    assert len(BG_EVIDENCE) >= 8
    assert any(r["id"] == "BG-REAL-EVAL" for r in BG_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN17" and r["decision"] == "SKIP"
        for r in BG_SCOREBOARD
    )
    assert any(r["id"] == "H-UNARYINT" for r in BG_SCOREBOARD)
    assert any(r["id"] == "H-SHIPPUB" for r in BG_SCOREBOARD)
    assert "H-CTXBG" in BG_REPORT_MARKERS
    assert "anti-FP" in BG_REPORT_MARKERS
    assert "ABSTAIN" in BG_REPORT_MARKERS
    assert "span-fallback" in BG_REPORT_MARKERS
    assert "true_continue" in BG_REPORT_MARKERS
    assert "BG-FOREVER" in BG_REPORT_MARKERS
    assert "over-refuse" in BG_REPORT_MARKERS
    assert "utilization" in BG_REPORT_MARKERS
    assert "SKIP" in BG_REPORT_MARKERS
    assert "H-NANOGEN6" in BG_REPORT_MARKERS
    assert "H-NANOGEN16" in BG_REPORT_MARKERS
    assert "H-NANOGEN17" in BG_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BG_EVIDENCE}
    out = decide_bg_report(ok)
    assert out.startswith("PROMOTE")
    assert BG_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BG_EVIDENCE}
    miss = "docs/results/nano-lm/wave-bg-summary.md"
    ok[miss] = False
    out = decide_bg_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_bg_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-UNARYINT**" in body
    assert "**H-SHIPPUB**" in body
    assert "**H-NANOGEN17**" in body
    assert "**H-NANOGEN16**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BG-REAL-EVAL**" in body
    assert "BG-FOREVER" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "SKIP" in body
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
    body = render_paper_lab_wave_bg()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BG-REAL-EVAL" in body
    assert "H-NANOGEN17" in body
    assert "SKIP" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN16" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "BG-FOREVER" in body
    assert "over-refuse" in body.lower()
    assert "utilization" in body.lower() or "util" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
