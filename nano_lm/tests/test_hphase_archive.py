"""Contract: H-ABS-PHASE smoke KILL is archived with identity lesson."""

from __future__ import annotations

from pathlib import Path

ARCHIVE = Path("docs/results/nano-lm/archive/hphase-phase.md")


def test_given_archive_when_read_then_kill_and_lesson() -> None:
    assert ARCHIVE.is_file()
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "KILL" in text
    assert "identity" in text.lower()
    assert "purged" in text.lower()
    assert "-14.8854" in text
    assert "-16.2692" in text
    assert "mean_abs_theta" in text or "|θ|" in text or "theta" in text.lower()
    assert "H-Q-ENTPOS" in text
