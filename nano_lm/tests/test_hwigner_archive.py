"""Contract: H-Q-WIGNER smoke KILL is archived with identity lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hwigner-wigner.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "identity" in text.lower()
    assert "purged" in text.lower()
    assert "-14.8854" in text
    assert "0.333" in text or "neg_mass" in text.lower()
    assert "H-ABS-CHRONO" in text
