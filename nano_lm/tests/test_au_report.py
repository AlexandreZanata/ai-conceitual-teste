"""Contract: Wave AU REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from au_report_ops import (
    AU_EVIDENCE,
    AU_ID,
    AU_REPORT_MARKERS,
    AU_SCOREBOARD,
    AU_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_au_report,
    realeval_section_ok,
    render_paper_lab_wave_au,
    render_wave_au_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_au5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU5 AU-REPORT
    assert AU_ID == "AU-REPORT"
    assert "not unlabeled open chat" in AU_THESIS.lower()
    assert "NANOGEN5" in AU_THESIS
    assert "5.5" in AU_THESIS
    assert "strict" in AU_THESIS.lower()
    assert len(AU_EVIDENCE) >= 8
    assert any(r["id"] == "AU-REAL-EVAL" for r in AU_SCOREBOARD)
    assert any(r["id"] == "H-NANOGEN5" for r in AU_SCOREBOARD)
    assert any(r["id"] == "H-PRODHARD" for r in AU_SCOREBOARD)
    assert "H-SHIPREAL" in AU_REPORT_MARKERS
    assert "anti-FP" in AU_REPORT_MARKERS
    assert "ABSTAIN" in AU_REPORT_MARKERS
    assert "gibberish-tail" in AU_REPORT_MARKERS
    assert "STRICT" in AU_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AU_EVIDENCE}
    out = decide_au_report(ok)
    assert out.startswith("PROMOTE")
    assert AU_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AU_EVIDENCE}
    miss = "docs/results/nano-lm/wave-au-summary.md"
    ok[miss] = False
    out = decide_au_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_au_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODHARD**" in body
    assert "**H-NANOGEN5**" in body
    assert "**AU-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "snippet-prefix" in body
    assert "gibberish-tail" in body
    assert "5.5" in body
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_au()
    assert "COMPLETE" in body and "FROZEN" in body
    assert "not unlabeled open chat" in body
    assert "AU-REAL-EVAL" in body
    assert "H-NANOGEN5" in body
    assert "5.5" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "snippet-prefix" in body
    assert "gibberish-tail" in body
    assert "≤5M" in body or "5M" in body
