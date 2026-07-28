"""Contract: Wave BC REPORT closeout (summary + paper-lab + anti-FP)."""

from __future__ import annotations

from bc_report_ops import (
    BC_EVIDENCE,
    BC_ID,
    BC_REPORT_MARKERS,
    BC_SCOREBOARD,
    BC_THESIS,
    SHIP_CLAIM,
    antifp_section_ok,
    decide_bc_report,
    realeval_section_ok,
    render_paper_lab_wave_bc,
    render_wave_bc_summary,
    report_markers_ok,
    scoreboard_ok,
)


def test_given_contract_when_constants_then_match_bc6_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §9 BC6 BC-REPORT
    assert BC_ID == "BC-REPORT"
    assert "not unlabeled open chat" in BC_THESIS.lower()
    assert "NANOGEN13" in BC_THESIS
    assert "DEFER" in BC_THESIS
    assert "OPSFAM" in BC_THESIS
    assert "FASTLIFT" in BC_THESIS
    assert "CTXLIFT2" in BC_THESIS
    assert "BC-FOREVER" in BC_THESIS or "forever" in BC_THESIS.lower()
    assert len(BC_EVIDENCE) >= 8
    assert any(r["id"] == "BC-REAL-EVAL" for r in BC_SCOREBOARD)
    assert any(
        r["id"] == "H-NANOGEN13" and r["decision"] == "DEFER"
        for r in BC_SCOREBOARD
    )
    assert any(r["id"] == "H-OPSFAM" for r in BC_SCOREBOARD)
    assert "H-CTXLIFT2" in BC_REPORT_MARKERS
    assert "anti-FP" in BC_REPORT_MARKERS
    assert "ABSTAIN" in BC_REPORT_MARKERS
    assert "span-fallback" in BC_REPORT_MARKERS
    assert "true_continue" in BC_REPORT_MARKERS
    assert "BC-FOREVER" in BC_REPORT_MARKERS
    assert "over-refuse" in BC_REPORT_MARKERS
    assert "H-NANOGEN6" in BC_REPORT_MARKERS
    assert "H-NANOGEN12" in BC_REPORT_MARKERS
    assert "snippet-prefix" in SHIP_CLAIM
    assert "gibberish-tail" in SHIP_CLAIM
    assert "product layer" in SHIP_CLAIM


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in BC_EVIDENCE}
    out = decide_bc_report(ok)
    assert out.startswith("PROMOTE")
    assert BC_ID in out


def test_given_missing_summary_when_decide_then_kill() -> None:
    ok = {p: True for p in BC_EVIDENCE}
    miss = "docs/results/nano-lm/wave-bc-summary.md"
    ok[miss] = False
    out = decide_bc_report(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_rendered_summary_when_markers_then_ok() -> None:
    body = render_wave_bc_summary()
    assert report_markers_ok(body) is True
    assert scoreboard_ok(body) is True
    assert antifp_section_ok(body) is True
    assert realeval_section_ok(body) is True
    assert "**H-OPSFAM**" in body
    assert "**H-NANOGEN13**" in body
    assert "**H-NANOGEN12**" in body
    assert "**H-NANOGEN6**" in body
    assert "**BC-REAL-EVAL**" in body
    assert "BC-FOREVER" in body
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
    body = render_paper_lab_wave_bc()
    assert "COMPLETE" in body
    assert "not unlabeled open chat" in body
    assert "BC-REAL-EVAL" in body
    assert "H-NANOGEN13" in body
    assert "DEFER" in body
    assert "H-NANOGEN6" in body
    assert "H-NANOGEN12" in body
    assert "HOLD" in body
    assert "span-fallback" in body
    assert "BC-FOREVER" in body
    assert "over-refuse" in body.lower()
    assert "anti-FP" in body
    assert "AF packaged stack" in body
    assert "≤5M" in body or "5M" in body
