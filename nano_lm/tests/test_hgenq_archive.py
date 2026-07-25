"""Contract: H-GENQ-ABS smoke+formal KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hgenq-amplitude.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "identity" in text.lower() or "single-slot" in text.lower()
    assert "purged" in text.lower()
    assert "H-GENC" in text or "GENC" in text
    assert "-13.9039" in text
    assert "H-DIST" in text or "distill" in text.lower()
