"""Contract: H-TCACHE smoke+formal PROMOTE reports exist with forwards↓."""

from __future__ import annotations

from pathlib import Path

SMOKE = Path("docs/results/nano-lm/htcache-tcache.md")
FORMAL = Path("docs/results/nano-lm/formal-htcache-tcache.md")


def test_given_smoke_when_read_then_promote() -> None:
    assert SMOKE.is_file()
    text = SMOKE.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "forwards" in text.lower()
    assert "TCACHE" in text


def test_given_formal_when_read_then_promote() -> None:
    assert FORMAL.is_file()
    text = FORMAL.read_text(encoding="utf-8")
    assert "PROMOTE" in text
    assert "forwards↓" in text or "forwards" in text.lower()
    assert "-9.6957" in text or "-10.3613" in text
    assert "31.2%" in text or "drop=" in text
