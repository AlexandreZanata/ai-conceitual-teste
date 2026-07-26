"""Contract: H-GENCACHE archive records smoke KILL lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hgencache-gencache.md")


def test_given_archive_when_read_then_kill_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "story" in text.lower()
    assert "-14.7412" in text or "Pareto" in text
    assert "QPFB2" in text
    assert "mem" in text.lower()
