"""Contract: H-STREAM archive records formal KILL lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hstream-stream.md")


def test_given_archive_when_read_then_kill_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story collapse" in text.lower() or "collapse" in text
    assert "-9.737" in text or "-10.872" in text
    assert "parent=prev" in text.lower() or "previous" in text.lower()
