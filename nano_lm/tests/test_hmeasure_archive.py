"""Contract: H-Q-MEASURE smoke KILL is archived with code↓ lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hmeasure-measure.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "code_lp" in text
    assert "purged" in text.lower()
    assert "-14.8854" in text
    assert "-18.0466" in text
    assert "switches" in text.lower()
    assert "H-Q-TELE" in text
