"""Contract: Wave Z0 export public note + summary exist."""

from __future__ import annotations

from pathlib import Path

EXPORT = Path("docs/results/nano-lm/wave-z-export.md")
SUMMARY = Path("docs/results/nano-lm/wave-z-summary.md")


def test_given_export_doc_when_read_then_done() -> None:
    assert EXPORT.is_file()
    text = EXPORT.read_text(encoding="utf-8")
    assert "DONE" in text
    assert "champion-qpfb2-v0" in text
    assert "H-ABS-QPFB2" in text


def test_given_summary_when_read_then_z0_done_z6_complete() -> None:
    assert SUMMARY.is_file()
    text = SUMMARY.read_text(encoding="utf-8")
    assert "Z0" in text and "DONE" in text
    assert "Z6" in text and "DONE" in text
    assert "COMPLETE" in text
    assert "H-ZWRAP" in text
