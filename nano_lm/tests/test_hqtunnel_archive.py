"""Contract: H-Q-TUNNEL smoke KILL is archived with identity lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hqtunnel-tunnel.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "identity" in text.lower()
    assert "story_lp" in text or "story_teacher" in text
    assert "code_lp" in text or "code_teacher" in text
    assert "purged" in text.lower()
    assert "-14.8854" in text
    assert "-16.2692" in text
    assert "H-Q-BELL" in text
