"""Contract: H-Q-ANNEAL smoke KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hqanneal-anneal.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story_lp" in text or "story_teacher" in text
    assert "code_lp" in text or "code_teacher" in text
    assert "purged" in text.lower()
    assert "-14.8854" in text
    assert "-14.9766" in text
    assert "-10.5057" in text
