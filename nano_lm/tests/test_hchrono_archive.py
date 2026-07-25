"""Contract: H-ABS-CHRONO smoke KILL is archived with code↓ lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hchrono-chrono.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "code_lp" in text
    assert "purged" in text.lower()
    assert "-16.2692" in text
    assert "-17.9939" in text
    assert "shuffle" in text.lower() or "0.85" in text
    assert "H-ABS-MIRROR" in text
