"""Contract: H-ABS-CSAFE smoke KILL is archived with story↓ / low-elig lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hcsafe-csafe.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story_lp" in text
    assert "purged" in text.lower()
    assert "-15.8695" in text or "-14.9354" in text
    assert "elig" in text.lower() or "n_elig" in text
    assert "parent" in text.lower()
    assert "HOLD" in text or "new H-ID" in text or "fallback" in text.lower()
