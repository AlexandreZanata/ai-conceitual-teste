"""Contract: Wave Z6 public HITL report + paper-lab exist with thesis."""

from __future__ import annotations

from pathlib import Path

from z6_ops import Z6_THESIS, report_markers_ok

REPORT = Path("docs/results/nano-lm/wave-z-hitl.md")
PAPER = Path("docs/results/nano-lm/paper-lab-wave-z.md")


def test_given_hitl_report_when_read_then_complete_thesis() -> None:
    assert REPORT.is_file()
    text = REPORT.read_text(encoding="utf-8")
    assert "COMPLETE" in text
    assert report_markers_ok(text)
    assert "H-ZWRAP" in text
    assert "wave-z-hitl-z4" in text


def test_given_paper_lab_when_read_then_one_liner() -> None:
    assert PAPER.is_file()
    text = PAPER.read_text(encoding="utf-8")
    assert "PFB recipes" in text or "interactive" in text
    assert "H-ZWRAP" in text
    # Thesis fragment must appear for external readers.
    assert "error-bank" in text or "error bank" in text.lower()
    assert "≠" in Z6_THESIS
