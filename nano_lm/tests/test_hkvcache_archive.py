"""Contract: H-KVCACHE-Q archive records smoke KILL lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hkvcache-kvcache.md")


def test_given_archive_when_read_then_kill_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "ttft" in text.lower() or "first-token" in text.lower()
    assert "3.08" in text or "warm" in text.lower()
    assert "QT" in text or "session" in text.lower()
