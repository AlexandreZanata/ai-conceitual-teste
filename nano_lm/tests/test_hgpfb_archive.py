"""Contract: H-ABS-GPFB archive records smoke KILL lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hgpfb-gpfb.md")


def test_given_archive_when_read_then_kill_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "code_lp" in text
    assert "-16.1024" in text or "GENC" in text
    assert "k=2" in text.lower() or "K=2" in text
