"""Contract: Wave AW REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from aw_report_ops import (
    AW_EVIDENCE,
    AW_ID,
    AW_REPORT_MARKERS,
    AW_SCOREBOARD,
    AW_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_aw_report,
    realeval_section_ok,
    render_paper_lab_wave_aw,
    render_wave_aw_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_aw5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §2 AW5 AW-REPORT
    assert AW_ID == "AW-REPORT"
    assert "not unlabeled open chat" in AW_THESIS.lower()
    assert "NANOGEN7" in AW_THESIS
    assert "HOLD" in AW_THESIS
    assert "PRODKEEP" in AW_THESIS
    assert "SHIPKEEP" in AW_THESIS
    assert "TAC" in AW_THESIS or "TAC" in AW_REPORT_MARKERS
    assert len(AW_EVIDENCE) >= 8
    assert any(r["id"] == "AW-REAL-EVAL" for r in AW_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN7" and r["decision"] == "HOLD" for r in AW_SCOREBOARD
    )
    assert any(r["id"] == "H-PRODKEEP" for r in AW_SCOREBOARD)
    assert "H-SHIPKEEP" in AW_REPORT_MARKERS
    assert "anti-FP" in AW_REPORT_MARKERS
    assert "ABSTAIN" in AW_REPORT_MARKERS
    assert "span-fallback" in AW_REPORT_MARKERS
    assert "true_continue" in AW_REPORT_MARKERS
    assert "TAC" in AW_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AW_EVIDENCE}
    out = decide_aw_report(ok)
    assert out.startswith("PROMOTE")
    assert AW_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AW_EVIDENCE}
    miss = "docs/results/nano-lm/wave-aw-summary.md"
    ok[miss] = False
    out = decide_aw_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_aw_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODKEEP**" in body
    assert "**H-NANOGEN7**" in body
    assert "**AW-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "TAC" in body
    assert "HOLD" in body
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_aw()
    assert "RESEARCH COMPLETE" in body or "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "AW-REAL-EVAL" in body
    assert "H-NANOGEN7" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "TAC" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
