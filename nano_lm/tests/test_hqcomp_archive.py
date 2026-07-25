"""Contract: H-QCOMP formal KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hqcomp-shadow-kv.md")
FORMAL = Path("docs/results/nano-lm/archive/formal-hqcomp-shadow-kv.md")
SMOKE = Path("docs/results/nano-lm/archive/hqcomp-shadow-kv-smoke.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    assert FORMAL.is_file()
    assert SMOKE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story" in text.lower()
    assert "code_teacher_lp" in text or "code_lp" in text
    assert "purged" in text.lower()
    assert "−11.0989" in text or "-11.0989" in text
    assert "−10.3233" in text or "-10.3233" in text
    assert "65536" in text
    assert "PROMOTE" in SMOKE.read_text(encoding="utf-8")
    assert "KILL" in FORMAL.read_text(encoding="utf-8")
