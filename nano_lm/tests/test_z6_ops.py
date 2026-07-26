"""Contract: Wave Z6 report gate + thesis markers."""

from __future__ import annotations

from z6_ops import (
    Z6_EVIDENCE,
    Z6_ID,
    Z6_REPORT_MARKERS,
    Z6_THESIS,
    decide_z6,
    report_markers_ok,
)


def test_given_all_evidence_when_decide_then_promote() -> None:
    ok = {p: True for p in Z6_EVIDENCE}
    out = decide_z6(ok)
    assert out.startswith("PROMOTE")
    assert Z6_ID in out
    assert "interactive" in Z6_THESIS.lower() or "≠" in Z6_THESIS


def test_given_missing_report_when_decide_then_kill() -> None:
    ok = {p: True for p in Z6_EVIDENCE}
    miss = "docs/results/nano-lm/wave-z-hitl.md"
    ok[miss] = False
    out = decide_z6(ok)
    assert out.startswith("KILL")
    assert miss in out


def test_given_thesis_text_when_markers_then_ok() -> None:
    # Minimal body covering Z6_REPORT_MARKERS (contract source: pesquisa §8 #5).
    body = (
        "Wave Z COMPLETE. PFB recipes are not an interactive LM. "
        "Product is H-ZWRAP WRAP_LOOKUP; H-ZERR is story-safe CE. "
        "Z1 period collapse; DEPL-Y frozen; error-bank loop."
    )
    assert report_markers_ok(body) is True
    assert "H-ZWRAP" in Z6_REPORT_MARKERS


def test_given_thin_text_when_markers_then_fail() -> None:
    assert report_markers_ok("PFB only") is False
