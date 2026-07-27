"""Contract: Wave AT REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from at_report_ops import (
    AT_EVIDENCE,
    AT_ID,
    AT_REPORT_MARKERS,
    AT_SCOREBOARD,
    AT_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_at_report,
    realeval_section_ok,
    render_paper_lab_wave_at,
    render_wave_at_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_at5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT5 AT-REPORT
    assert AT_ID == "AT-REPORT"
    assert "not unlabeled open chat" in AT_THESIS.lower()
    assert "NANOGEN4" in AT_THESIS
    assert "5.5" in AT_THESIS
    assert len(AT_EVIDENCE) >= 8
    assert any(r["id"] == "AT-REAL-EVAL" for r in AT_SCOREBOARD)
    assert any(r["id"] == "H-NANOGEN4" for r in AT_SCOREBOARD)
    assert any(r["id"] == "H-PRODREG" for r in AT_SCOREBOARD)
    assert "H-SHIPAPP" in AT_REPORT_MARKERS
    assert "anti-FP" in AT_REPORT_MARKERS
    assert "ABSTAIN" in AT_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AT_EVIDENCE}
    out = decide_at_report(ok)
    assert out.startswith("PROMOTE")
    assert AT_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AT_EVIDENCE}
    miss = "docs/results/nano-lm/wave-at-summary.md"
    ok[miss] = False
    out = decide_at_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_at_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODREG**" in body
    assert "**H-NANOGEN4**" in body
    assert "**AT-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "snippet-prefix" in body
    assert "5.5" in body
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_at()
    assert "COMPLETE" in body and "FROZEN" in body
    assert "not unlabeled open chat" in body
    assert "AT-REAL-EVAL" in body
    assert "H-NANOGEN4" in body
    assert "5.5" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "snippet-prefix" in body
    assert "≤5M" in body or "5M" in body
