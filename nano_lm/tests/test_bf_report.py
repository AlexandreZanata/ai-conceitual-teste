"""Contract: Wave BF REPORT closeout (summary + paper-lab + anti-FP · util)."""

from __future__ import annotations

from bf_report_ops import (
    BF_EVIDENCE,
    BF_ID,
    BF_REPORT_MARKERS,
    BF_SCOREBOARD,
    BF_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bf_report,
    realeval_section_ok,
    render_paper_lab_wave_bf,
    render_wave_bf_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_bf7_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BF7 BF-REPORT
    assert BF_ID == "BF-REPORT"
    assert "not unlabeled open chat" in BF_THESIS.lower()
    assert "NANOGEN16" in BF_THESIS
    assert "SKIP" in BF_THESIS
    assert "PREDINT" in BF_THESIS
    assert "SHIPUSE2" in BF_THESIS
    assert "FASTBF" in BF_THESIS
    assert "CTXBF" in BF_THESIS
    assert "BF-FOREVER" in BF_THESIS or "forever" in BF_THESIS.lower()
    assert len(BF_EVIDENCE) >= 8
    assert any(r["id"] == "BF-REAL-EVAL" for r in BF_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN16" and r["decision"] == "SKIP"
        for r in BF_SCOREBOARD
    )
    assert any(r["id"] == "H-PREDINT" for r in BF_SCOREBOARD)
    assert any(r["id"] == "H-SHIPUSE2" for r in BF_SCOREBOARD)
    assert "H-CTXBF" in BF_REPORT_MARKERS
    assert "anti-FP" in BF_REPORT_MARKERS
    assert "ABSTAIN" in BF_REPORT_MARKERS
    assert "span-fallback" in BF_REPORT_MARKERS
    assert "true_continue" in BF_REPORT_MARKERS
    assert "BF-FOREVER" in BF_REPORT_MARKERS
    assert "over-refuse" in BF_REPORT_MARKERS
    assert "utilization" in BF_REPORT_MARKERS
    assert "SKIP" in BF_REPORT_MARKERS
    assert "H-NANOGEN6" in BF_REPORT_MARKERS
    assert "H-NANOGEN15" in BF_REPORT_MARKERS
    assert "H-NANOGEN16" in BF_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BF_EVIDENCE}
    out = decide_bf_report(ok)
    assert out.startswith("PROMOTE")
    assert BF_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BF_EVIDENCE}
    miss = "docs/results/nano-lm/wave-bf-summary.md"
    ok[miss] = False
    out = decide_bf_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_bf_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PREDINT**" in body
    assert "**H-SHIPUSE2**" in body
    assert "**H-NANOGEN16**" in body
    assert "**H-NANOGEN15**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BF-REAL-EVAL**" in body
    assert "BF-FOREVER" in body
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
    body = render_paper_lab_wave_bf()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BF-REAL-EVAL" in body
    assert "H-NANOGEN16" in body
    assert "SKIP" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN15" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "BF-FOREVER" in body
    assert "over-refuse" in body.lower()
    assert "utilization" in body.lower() or "util" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
