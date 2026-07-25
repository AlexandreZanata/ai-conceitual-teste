"""Contract: H-ABS-ORACLE1 smoke KILL is archived with effect sizes."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/horacle1-oracle.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "code_lp" in text
    assert "RAG" in text
    assert "purged" in text.lower()
    assert "-16.2692" in text
    assert "-16.4182" in text
    assert "-16.9977" in text
    assert "H-ABS-DNA" in text
