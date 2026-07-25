"""Contract: H-ABS-GPFB4 smoke+formal PROMOTE reports exist with dual-gate win."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/hgpfb4-gpfb4.md")
FORMAL = Path("docs/results/nano-lm/formal-hgpfb4-gpfb4.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "GENC" in text
    assert "GPFB" in text or "gpfb" in text.lower()


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "story" in text.lower()
    assert "code" in text.lower()
    assert "parent" in text.lower()
