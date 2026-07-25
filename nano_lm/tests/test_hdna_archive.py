"""Contract: H-ABS-DNA smoke KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hdna-dna.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story_lp" in text
    assert "code_lp" in text
    assert "purged" in text.lower()
    assert "-14.8854" in text
    assert "-15.6840" in text
    assert "-15.7925" in text
    assert "H-ABS-DEBATE" in text
