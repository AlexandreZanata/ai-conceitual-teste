"""Contract: H-CKD smoke KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hckd-code-kd.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "code_teacher_lp" in text
    assert "soft" in text.lower() or "soft-KD" in text
    assert "purged" in text.lower()
    assert "-16.2692" in text
    assert "-19.2446" in text
