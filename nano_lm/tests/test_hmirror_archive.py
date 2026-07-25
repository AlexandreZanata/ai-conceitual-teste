"""Contract: H-ABS-MIRROR formal KILL is archived with story↓ lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hmirror-mirror.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story_lp" in text
    assert "purged" in text.lower()
    assert "-12.9699" in text or "-10.3733" in text
    assert "PROMOTE" in text  # smoke provisional noted
    assert "exhausted" in text.lower() or "HOLD" in text or "new H-ID" in text
