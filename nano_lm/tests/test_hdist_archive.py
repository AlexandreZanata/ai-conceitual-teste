"""Contract: H-DIST smoke KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hdist-distill.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "code_teacher_lp" in text or "code_lp" in text
    assert "shared" in text.lower()
    assert "purged" in text.lower()
    assert "-16.2692" in text
    assert "-18.5189" in text
    assert "gpt-neo" in text.lower() or "GPT-Neo" in text
