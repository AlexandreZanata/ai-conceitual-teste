"""Contract: Wave BD REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from bd_report_ops import (
    BD_EVIDENCE,
    BD_ID,
    BD_REPORT_MARKERS,
    BD_SCOREBOARD,
    BD_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bd_report,
    realeval_section_ok,
    render_paper_lab_wave_bd,
    render_wave_bd_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_bd6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BD6 BD-REPORT
    assert BD_ID == "BD-REPORT"
    assert "not unlabeled open chat" in BD_THESIS.lower()
    assert "NANOGEN14" in BD_THESIS
    assert "DEFER" in BD_THESIS
    assert "SEMINT" in BD_THESIS
    assert "FASTGAIN" in BD_THESIS
    assert "CTXGAIN" in BD_THESIS
    assert "BD-FOREVER" in BD_THESIS or "forever" in BD_THESIS.lower()
    assert len(BD_EVIDENCE) >= 8
    assert any(r["id"] == "BD-REAL-EVAL" for r in BD_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN14" and r["decision"] == "DEFER"
        for r in BD_SCOREBOARD
    )
    assert any(r["id"] == "H-SEMINT" for r in BD_SCOREBOARD)
    assert "H-CTXGAIN" in BD_REPORT_MARKERS
    assert "anti-FP" in BD_REPORT_MARKERS
    assert "ABSTAIN" in BD_REPORT_MARKERS
    assert "span-fallback" in BD_REPORT_MARKERS
    assert "true_continue" in BD_REPORT_MARKERS
    assert "BD-FOREVER" in BD_REPORT_MARKERS
    assert "over-refuse" in BD_REPORT_MARKERS
    assert "H-NANOGEN6" in BD_REPORT_MARKERS
    assert "H-NANOGEN13" in BD_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BD_EVIDENCE}
    out = decide_bd_report(ok)
    assert out.startswith("PROMOTE")
    assert BD_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BD_EVIDENCE}
    miss = "docs/results/nano-lm/wave-bd-summary.md"
    ok[miss] = False
    out = decide_bd_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_bd_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-SEMINT**" in body
    assert "**H-NANOGEN14**" in body
    assert "**H-NANOGEN13**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BD-REAL-EVAL**" in body
    assert "BD-FOREVER" in body
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
    body = render_paper_lab_wave_bd()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BD-REAL-EVAL" in body
    assert "H-NANOGEN14" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN13" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "BD-FOREVER" in body
    assert "over-refuse" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
