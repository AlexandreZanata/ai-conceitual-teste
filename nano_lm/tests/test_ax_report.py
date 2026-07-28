"""Contract: Wave AX REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from ax_report_ops import (
    AX_EVIDENCE,
    AX_ID,
    AX_REPORT_MARKERS,
    AX_SCOREBOARD,
    AX_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_ax_report,
    realeval_section_ok,
    render_paper_lab_wave_ax,
    render_wave_ax_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_ax5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AX5 AX-REPORT
    assert AX_ID == "AX-REPORT"
    assert "not unlabeled open chat" in AX_THESIS.lower()
    assert "NANOGEN8" in AX_THESIS
    assert "DEFER" in AX_THESIS
    assert "PRODNAT" in AX_THESIS
    assert "SHIPUX" in AX_THESIS
    assert "NANOGEN6" in AX_THESIS or "NANOGEN6" in AX_REPORT_MARKERS
    assert "NANOGEN7" in AX_THESIS or "NANOGEN7" in AX_REPORT_MARKERS
    assert len(AX_EVIDENCE) >= 8
    assert any(r["id"] == "AX-REAL-EVAL" for r in AX_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN8" and r["decision"] == "DEFER"
        for r in AX_SCOREBOARD
    )
    assert any(r["id"] == "H-PRODNAT" for r in AX_SCOREBOARD)
    assert "H-SHIPUX" in AX_REPORT_MARKERS
    assert "anti-FP" in AX_REPORT_MARKERS
    assert "ABSTAIN" in AX_REPORT_MARKERS
    assert "span-fallback" in AX_REPORT_MARKERS
    assert "true_continue" in AX_REPORT_MARKERS
    assert "hard-natural" in AX_REPORT_MARKERS
    assert "H-NANOGEN6" in AX_REPORT_MARKERS
    assert "H-NANOGEN7" in AX_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in AX_EVIDENCE}
    out = decide_ax_report(ok)
    assert out.startswith("PROMOTE")
    assert AX_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in AX_EVIDENCE}
    miss = "docs/results/nano-lm/wave-ax-summary.md"
    ok[miss] = False
    out = decide_ax_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_ax_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-PRODNAT**" in body
    assert "**H-NANOGEN8**" in body
    assert "**H-NANOGEN6**" in body
    assert "**H-NANOGEN7**" in body
    assert "**AX-REAL-EVAL**" in body
    assert "Metric" in body
    assert "not generative IQ" in body
    assert "LOOKUP" in body and "PEAK" in body and "DECODE" in body
    assert "ABSTAIN" in body
    assert "span-fallback" in body
    assert "true_continue" in body
    assert "DEFER" in body
    assert "HOLD" in body
    assert "hard-natural" in body
    assert SHIP_CLAIM.split("—")[0].strip() in body


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("ABSTAIN only") is False
    assert scoreboard_ok("no table") is False
    assert antifp_section_ok("LOOKUP only") is False
    assert realeval_section_ok("no section") is False


def test_given_paper_lab_when_render_then_complete() -> None:
    body = render_paper_lab_wave_ax()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "AX-REAL-EVAL" in body
    assert "H-NANOGEN8" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN7" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "hard-natural" in body
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
